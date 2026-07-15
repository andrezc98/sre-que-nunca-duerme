#!/usr/bin/env python3
"""Benchmark de cerebros SRE: escenarios reales x modelos, métricas completas.

Por cada (escenario, cerebro): aplica el manifiesto roto, espera que el estado
se asiente, cambia el cerebro del sre-agent, pregunta vía A2A y captura:
tokens (in/out, por paso), latencia, pasos (tool calls), errores de tool
auto-corregidos, y un match automático de causa raíz (verificable a mano).

Uso:
  python3 demo/bench/bench.py                    # todo x todo
  python3 demo/bench/bench.py --brains ollama-qwen bedrock-claude --scenarios imagepull
Resultados: demo/bench/results.jsonl (append; una línea por corrida)
Requiere los port-forwards del panel (kind:8083, eks:8084).
"""
import argparse
import json
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).parent

# cerebro -> (contexto kubectl, URL del kagent-controller).
# Los port-forwards los crea y destruye ESTE script (puertos propios 18083/18084):
# un pf compartido/reciclado puede quedar apuntando al cluster equivocado y
# el benchmark entero mide al agente incorrecto (nos pasó: 8083 quedó en EKS).
PF_PORTS = {"kind-kcd": 18083, "eks-demo": 18084}
BRAINS = {
    "ollama-qwen":      ("kind-kcd", "http://localhost:18083"),
    "qwen36-27b":       ("kind-kcd", "http://localhost:18083"),
    "glm-cloud":        ("kind-kcd", "http://localhost:18083"),
    "minimax-cloud":    ("kind-kcd", "http://localhost:18083"),
    "kimi-cloud":       ("kind-kcd", "http://localhost:18083"),
    "bedrock-claude":   ("eks-demo", "http://localhost:18084"),
    "bedrock-sonnet-5": ("eks-demo", "http://localhost:18084"),
    "bedrock-opus":     ("eks-demo", "http://localhost:18084"),
}

# USD por millón de tokens (in, out). 0 = local / plan flat.
PRICES = {
    "ollama-qwen": (0.0, 0.0),
    "qwen36-27b": (0.0, 0.0),
    "glm-cloud": (0.0, 0.0),      # ollama cloud: plan flat, no por token
    "minimax-cloud": (0.0, 0.0),
    "kimi-cloud": (0.0, 0.0),
    "bedrock-claude": (3.0, 15.0),
    "bedrock-sonnet-5": (3.0, 15.0),
    "bedrock-opus": (5.0, 25.0),
}

SCENARIOS = {
    "imagepull": {
        "grace": 40,
        "pod": "roto-imagen",
        "expect": ["noexiste", "imagepull", "errimagepull", "no existe", "not found", "inexistente"],
        "manifest": {"apiVersion": "v1", "kind": "Pod",
                     "metadata": {"name": "roto-imagen", "namespace": "bench"},
                     "spec": {"containers": [{"name": "c", "image": "nginx:noexiste"}]}},
    },
    "crashloop": {
        "grace": 50,
        "pod": "roto-crash",
        "expect": ["crashloop", "exit", "código 1", "codigo 1", "falla el comando", "sale con error", "termina"],
        "manifest": {"apiVersion": "v1", "kind": "Pod",
                     "metadata": {"name": "roto-crash", "namespace": "bench"},
                     "spec": {"containers": [{"name": "c", "image": "busybox:1.36",
                                              "command": ["sh", "-c", "echo arrancando; sleep 2; echo ERROR fatal: config invalida; exit 1"]}]}},
    },
    "oom": {
        "grace": 60,
        "pod": "roto-oom",
        "expect": ["oom", "memoria", "memory", "límite", "limite", "137"],
        "manifest": {"apiVersion": "v1", "kind": "Pod",
                     "metadata": {"name": "roto-oom", "namespace": "bench"},
                     "spec": {"containers": [{"name": "c", "image": "python:3.12-alpine",
                                              "command": ["python", "-c", "a=[];\nwhile True: a.append(' '*10**6)"],
                                              "resources": {"limits": {"memory": "64Mi"}}}]}},
    },
    "badconfig": {
        "grace": 30,
        "pod": "roto-config",
        "expect": ["configmap", "config-inexistente", "no existe", "not found", "createcontainerconfig"],
        "manifest": {"apiVersion": "v1", "kind": "Pod",
                     "metadata": {"name": "roto-config", "namespace": "bench"},
                     "spec": {"containers": [{"name": "c", "image": "nginx:1.27",
                                              "envFrom": [{"configMapRef": {"name": "config-inexistente"}}]}]}},
    },
    "probefail": {
        "grace": 45,
        "pod": "roto-probe",
        "expect": ["readiness", "probe", "8080", "puerto", "sonda"],
        "manifest": {"apiVersion": "v1", "kind": "Pod",
                     "metadata": {"name": "roto-probe", "namespace": "bench"},
                     "spec": {"containers": [{"name": "c", "image": "nginx:1.27",
                                              "readinessProbe": {"httpGet": {"path": "/", "port": 8080},
                                                                 "periodSeconds": 5}}]}},
    },
    "unschedulable": {
        "grace": 25,
        "pod": "roto-pending",
        "expect": ["insufficient", "cpu", "pending", "no hay nodo", "recursos", "unschedulable", "programar"],
        "manifest": {"apiVersion": "v1", "kind": "Pod",
                     "metadata": {"name": "roto-pending", "namespace": "bench"},
                     "spec": {"containers": [{"name": "c", "image": "nginx:1.27",
                                              "resources": {"requests": {"cpu": "64"}}}]}},
    },
}

PROMPT = ("En el namespace 'bench' hay un pod llamado '{pod}' con problemas. "
          "Diagnostica la CAUSA RAÍZ exacta usando tus herramientas y propone el fix concreto. Sé breve.")


def sh(*cmd, ctx=None, check=True, stdin=None):
    full = ["kubectl"] + (["--context", ctx] if ctx else []) + list(cmd)
    return subprocess.run(full, input=stdin, capture_output=True, text=True, check=check)


def swap_brain(ctx: str, brain: str):
    sh("-n", "kagent", "patch", "agent", "sre-agent", "--type", "merge",
       "-p", json.dumps({"spec": {"declarative": {"modelConfig": brain}}}), ctx=ctx)
    time.sleep(5)
    sh("-n", "kagent", "rollout", "status", "deploy/sre-agent", "--timeout=180s", ctx=ctx)
    time.sleep(8)  # que el pod viejo suelte el puerto del service


def ask(url: str, text: str) -> tuple[dict, float]:
    payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send",
               "params": {"message": {"role": "user", "messageId": str(uuid.uuid4()),
                                      "parts": [{"kind": "text", "text": text}]}}}
    req = urllib.request.Request(url + "/api/a2a/kagent/sre-agent",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r).get("result", {}), time.time() - t0


def metrics(result: dict) -> dict:
    hist = result.get("history", [])
    tin = tout = steps = tool_errors = 0
    tools = []
    for msg in hist:
        u = (msg.get("metadata") or {}).get("kagent_usage_metadata") or {}
        tin += u.get("promptTokenCount", 0)
        tout += u.get("candidatesTokenCount", 0)
        for p in msg.get("parts", []):
            if p.get("kind") != "data":
                continue
            kt = (p.get("metadata") or {}).get("kagent_type")
            if kt == "function_call":
                steps += 1
                tools.append(p.get("data", {}).get("name", "?"))
            elif kt == "function_response":
                if (p.get("data", {}).get("response") or {}).get("isError"):
                    tool_errors += 1
    answer = "\n".join(p.get("text", "") for a in result.get("artifacts", [])
                       for p in a.get("parts", []) if p.get("kind") == "text")
    return {"tokens_in": tin, "tokens_out": tout, "steps": steps,
            "tool_errors": tool_errors, "tools": tools, "answer": answer}


def run(scenario: str, brain: str) -> dict:
    ctx, url = BRAINS[brain]
    sc = SCENARIOS[scenario]
    print(f"→ {scenario} × {brain} ({ctx})", flush=True)
    sh("create", "namespace", "bench", ctx=ctx, check=False)
    sh("-n", "bench", "delete", "pod", "--all", "--now", ctx=ctx, check=False)
    sh("apply", "-f", "-", ctx=ctx, stdin=json.dumps(sc["manifest"]))
    time.sleep(sc["grace"])
    swap_brain(ctx, brain)
    try:
        result, seconds = ask(url, PROMPT.format(pod=sc["pod"]))
        m = metrics(result)
        if not m["answer"].strip():  # respuesta vacía: reintenta una vez y guarda el crudo
            time.sleep(20)
            result, retry_secs = ask(url, PROMPT.format(pod=sc["pod"]))
            m = metrics(result)
            seconds += retry_secs
            if not m["answer"].strip():
                m["raw_debug"] = json.dumps(result, ensure_ascii=False)[:2000]
        error = None
    except Exception as e:
        m, seconds, error = {"tokens_in": 0, "tokens_out": 0, "steps": 0,
                             "tool_errors": 0, "tools": [], "answer": ""}, 0.0, f"{type(e).__name__}: {e}"
    pin, pout = PRICES[brain]
    cost = m["tokens_in"] / 1e6 * pin + m["tokens_out"] / 1e6 * pout
    causa_ok = any(k in m["answer"].lower() for k in sc["expect"])
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "scenario": scenario, "brain": brain,
           "seconds": round(seconds, 1), "cost_usd": round(cost, 6),
           "causa_ok_auto": causa_ok, "error": error, **m}
    with open(HERE / "results.jsonl", "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    ok = "✅" if causa_ok else ("💥" if error else "❌")
    print(f"  {ok} {row['seconds']}s · {row['steps']} pasos · "
          f"{row['tokens_in']}+{row['tokens_out']} tok · ${row['cost_usd']:.4f}", flush=True)
    sh("-n", "bench", "delete", "pod", "--all", "--now", ctx=ctx, check=False)
    return row


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--brains", nargs="+", default=list(BRAINS), choices=list(BRAINS))
    ap.add_argument("--scenarios", nargs="+", default=list(SCENARIOS), choices=list(SCENARIOS))
    args = ap.parse_args()
    contexts = {BRAINS[b][0] for b in args.brains}
    pfs = [subprocess.Popen(
        ["kubectl", "--context", c, "-n", "kagent", "port-forward",
         f"--address=127.0.0.1", "svc/kagent-controller", f"{PF_PORTS[c]}:8083"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for c in contexts]
    time.sleep(5)
    try:
        # agrupado por cluster para minimizar swaps de cerebro
        for scenario in args.scenarios:
            for brain in sorted(args.brains, key=lambda b: BRAINS[b][0]):
                run(scenario, brain)
    finally:
        for p in pfs:
            p.terminate()
    print(f"\nresultados en {HERE / 'results.jsonl'} — genera el reporte con: "
          f"python3 demo/bench/report.py")
