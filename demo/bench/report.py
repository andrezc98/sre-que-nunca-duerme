#!/usr/bin/env python3
"""Genera report.html desde results.jsonl: tiles por cerebro + carreras por escenario.

Veredicto humano opcional en verdicts.json (gana sobre el match automático):
  {"imagepull": {"ollama-qwen": {"veredicto": "correcto|parcial|fallo", "alucino": false}}}
"""
import html
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
PALETTE = ["#3987e5", "#199e70", "#c98500", "#008300", "#9085e9"]  # validado (dark)
ORDER = ["ollama-qwen", "glm-cloud", "bedrock-claude", "bedrock-sonnet-5", "bedrock-opus"]
LABEL = {"ollama-qwen": "Qwen 3.5 4B · local", "glm-cloud": "GLM 5.2 · Ollama Cloud",
         "bedrock-claude": "Claude Sonnet 4.6 · Bedrock", "bedrock-sonnet-5": "Claude Sonnet 5 · Bedrock",
         "bedrock-opus": "Claude Opus 4.8 · Bedrock"}
SCEN_TITLE = {"imagepull": "Imagen inexistente", "crashloop": "CrashLoopBackOff",
              "oom": "OOMKilled", "badconfig": "ConfigMap fantasma",
              "probefail": "Readiness probe rota", "unschedulable": "Pod imposible de programar"}
BADGE = {"correcto": ("✅", "Correcto"), "parcial": ("⚠️", "Parcial"),
         "fallo": ("❌", "Falló"), "alucino": ("👻", "Alucinó"), "error": ("💥", "Error")}


def load():
    rows = {}
    with open(HERE / "results.jsonl") as f:
        for line in f:
            r = json.loads(line)
            rows[(r["scenario"], r["brain"])] = r  # la última corrida gana
    verdicts = {}
    vf = HERE / "verdicts.json"
    if vf.exists():
        verdicts = json.loads(vf.read_text())
    return rows, verdicts


def verdict_of(r, verdicts):
    v = (verdicts.get(r["scenario"], {}) or {}).get(r["brain"], {})
    if r.get("error"):
        return "error", False
    if v.get("alucino"):
        return v.get("veredicto", "fallo"), True
    if "veredicto" in v:
        return v["veredicto"], False
    return ("correcto" if r["causa_ok_auto"] else "fallo"), False


def main():
    rows, verdicts = load()
    brains = [b for b in ORDER if any(k[1] == b for k in rows)]
    scenarios = sorted({k[0] for k in rows}, key=lambda s: list(SCEN_TITLE).index(s) if s in SCEN_TITLE else 99)
    color = {b: PALETTE[ORDER.index(b) % len(PALETTE)] for b in brains}

    per_brain = defaultdict(lambda: {"ok": 0, "n": 0, "cost": 0.0, "secs": 0.0})
    for r in rows.values():
        v, hall = verdict_of(r, verdicts)
        s = per_brain[r["brain"]]
        s["n"] += 1
        s["ok"] += (v == "correcto" and not hall)
        s["cost"] += r["cost_usd"]
        s["secs"] += r["seconds"]

    tiles = ""
    for b in brains:
        s = per_brain[b]
        pct = 100 * s["ok"] / s["n"] if s["n"] else 0
        cpd = ("$0" if s["cost"] == 0 else f"${s['cost'] / s['ok']:.4f}") if s["ok"] else "∞"
        tiles += f"""<div class=tile><div class=dot style="background:{color[b]}"></div>
<div class=tname>{html.escape(LABEL.get(b, b))}</div>
<div class=big>{pct:.0f}%</div><div class=sub>aciertos ({s['ok']}/{s['n']})</div>
<div class=sub2>{cpd} por diagnóstico correcto · {s['secs'] / max(s['n'], 1):.0f}s prom.</div></div>"""

    sections = ""
    for sc in scenarios:
        runs = [rows[(sc, b)] for b in brains if (sc, b) in rows]
        if not runs:
            continue
        maxs = max(r["seconds"] for r in runs) or 1
        lanes = ""
        for r in runs:
            v, hall = verdict_of(r, verdicts)
            icon, word = BADGE["alucino"] if hall else BADGE[v]
            w = max(6, 100 * r["seconds"] / maxs)
            dots = "".join(
                f'<span class=step title="{html.escape(t)}" style="left:{(i + 1) * 100 / (r["steps"] + 1):.0f}%"></span>'
                for i, t in enumerate(r["tools"]))
            lanes += f"""<div class=lane><div class=lname>{html.escape(LABEL.get(r['brain'], r['brain']))}</div>
<div class=track><div class=bar style="width:{w:.0f}%;background:{color[r['brain']]}">{dots}</div></div>
<div class=lmeta>{r['seconds']:.0f}s · {r['steps']} pasos · {r['tokens_in'] + r['tokens_out']} tok · ${r['cost_usd']:.4f}
 <span class=badge>{icon} {word}</span>{' · 🔁' + str(r['tool_errors']) if r['tool_errors'] else ''}</div></div>"""
        sections += f"<h2>{html.escape(SCEN_TITLE.get(sc, sc))}</h2>{lanes}"

    table = "<details><summary>datos y respuestas completas (revisión)</summary><table><tr><th>escenario</th><th>cerebro</th><th>veredicto</th><th>s</th><th>pasos</th><th>tok in/out</th><th>$</th><th>respuesta</th></tr>"
    for (sc, b), r in sorted(rows.items()):
        v, hall = verdict_of(r, verdicts)
        table += (f"<tr><td>{sc}</td><td>{b}</td><td>{'👻' if hall else ''}{v}</td><td>{r['seconds']}</td>"
                  f"<td>{r['steps']}</td><td>{r['tokens_in']}/{r['tokens_out']}</td><td>{r['cost_usd']:.4f}</td>"
                  f"<td class=ans>{html.escape((r.get('answer') or r.get('error') or '')[:600])}</td></tr>")
    table += "</table></details>"

    page = f"""<!doctype html><html lang=es><head><meta charset=utf-8>
<title>¿Cuánto modelo necesita un SRE?</title><style>
 body{{font-family:ui-monospace,Menlo,monospace;background:#1a1a19;color:#fff;margin:0;padding:2rem;max-width:70rem;margin-inline:auto}}
 h1{{font-size:1.3rem}} h1 em{{color:#c3c2b7;font-style:normal;font-size:.85rem;display:block;margin-top:.3rem}}
 h2{{font-size:1rem;color:#c3c2b7;margin:1.6rem 0 .6rem;border-top:1px solid #333;padding-top:1rem}}
 .tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.8rem;margin:1.2rem 0}}
 .tile{{background:#222220;border:1px solid #333;border-radius:8px;padding:1rem;position:relative}}
 .dot{{width:10px;height:10px;border-radius:50%;position:absolute;top:1rem;right:1rem}}
 .tname{{font-size:.75rem;color:#c3c2b7;min-height:2.2em}} .big{{font-size:2.3rem;font-weight:700;line-height:1.1}}
 .sub{{font-size:.75rem;color:#c3c2b7}} .sub2{{font-size:.72rem;color:#8b8a82;margin-top:.4rem}}
 .lane{{display:grid;grid-template-columns:13rem 1fr;gap:.6rem;align-items:center;margin:.45rem 0}}
 .lname{{font-size:.78rem;color:#fff;text-align:right}}
 .track{{position:relative}} .bar{{height:14px;border-radius:0 4px 4px 0;position:relative;min-width:8px}}
 .step{{position:absolute;top:50%;transform:translate(-50%,-50%);width:8px;height:8px;border-radius:50%;background:#fff;border:2px solid #1a1a19}}
 .lmeta{{grid-column:2;font-size:.72rem;color:#c3c2b7;margin-top:-2px}}
 .badge{{color:#fff}} details{{margin-top:2rem;font-size:.78rem}} summary{{cursor:pointer;color:#c3c2b7}}
 table{{border-collapse:collapse;margin-top:.8rem;width:100%}} td,th{{border:1px solid #333;padding:.3rem .5rem;text-align:left;vertical-align:top}}
 .ans{{max-width:28rem;color:#c3c2b7}}
</style></head><body>
<h1>🤖 ¿Cuánto modelo necesita un SRE?<em>mismo agente (kagent CRD) · mismas herramientas MCP · {len(scenarios)} incidentes reales · barra = latencia · puntos = tool calls</em></h1>
<div class=tiles>{tiles}</div>
{sections}
{table}
</body></html>"""
    out = HERE / "report.html"
    out.write_text(page)
    print(f"reporte: {out}")


if __name__ == "__main__":
    main()
