#!/usr/bin/env python3
"""Panel de demo: un agente, dos cerebros — lado a lado.

Sirve una página que manda la MISMA pregunta al sre-agent de dos clusters
(kind local con Qwen/Ollama y EKS con Claude/Bedrock) vía la API A2A del
kagent-controller, y muestra respuestas, herramientas usadas y tiempos.

Uso (dos port-forwards + este server, stdlib puro, cero dependencias):
  kubectl --context kind-kcd  -n kagent port-forward svc/kagent-controller 8083:8083 &
  kubectl --context eks-demo -n kagent port-forward svc/kagent-controller 8084:8083 &
  python3 demo/panel.py            # -> http://localhost:7777
"""
import json
import os
import time
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SIDES = {
    "local": os.environ.get("PANEL_LOCAL", "http://localhost:8083"),
    "eks": os.environ.get("PANEL_EKS", "http://localhost:8084"),
}
AGENT_PATH = "/api/a2a/kagent/sre-agent"

HTML = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>El SRE que Nunca Duerme</title>
<style>
 body{font-family:ui-monospace,Menlo,monospace;background:#0d1117;color:#e6edf3;margin:0;padding:1.5rem}
 h1{font-size:1.15rem;font-weight:600} h1 span{color:#7ee787}
 form{display:flex;gap:.5rem;margin:1rem 0}
 input{flex:1;padding:.7rem;background:#161b22;border:1px solid #30363d;border-radius:6px;color:#e6edf3;font:inherit}
 button{padding:.7rem 1.2rem;background:#238636;border:0;border-radius:6px;color:#fff;font:inherit;cursor:pointer}
 button:disabled{opacity:.5}
 .cols{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
 .card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem;min-height:12rem}
 .card h2{font-size:.95rem;margin:0 0 .5rem} .meta{color:#8b949e;font-size:.8rem;min-height:1.2rem}
 .tools{margin:.4rem 0} .tools code{background:#1f2937;border-radius:4px;padding:.1rem .4rem;margin-right:.3rem;font-size:.75rem;color:#79c0ff}
 pre{white-space:pre-wrap;word-wrap:break-word;font-size:.85rem;line-height:1.45;margin:.5rem 0 0}
 .err{color:#ffa198}
</style></head><body>
<h1>🤖 El SRE que Nunca Duerme — <span>un agente, dos cerebros</span></h1>
<form id=f><input id=q placeholder="p.ej.: ¿por qué falla el pod 'roto' en default?" autofocus>
<button id=b>Preguntar a ambos</button></form>
<div class=cols>
 <div class=card><h2>🖥️ kind (laptop) · Qwen 3.5 vía Ollama · $0</h2><div class=meta id=m-local></div><div class=tools id=t-local></div><pre id=r-local></pre></div>
 <div class=card><h2>☁️ EKS (Graviton5) · Claude vía Bedrock · Pod Identity</h2><div class=meta id=m-eks></div><div class=tools id=t-eks></div><pre id=r-eks></pre></div>
</div>
<script>
const f=document.getElementById('f'),q=document.getElementById('q'),b=document.getElementById('b');
async function ask(side,text){
 const m=document.getElementById('m-'+side),r=document.getElementById('r-'+side),t=document.getElementById('t-'+side);
 r.textContent='';t.innerHTML='';const t0=Date.now();m.textContent='pensando…';
 const tick=setInterval(()=>{m.textContent='pensando… '+((Date.now()-t0)/1000).toFixed(0)+'s'},500);
 try{
  const res=await fetch('/ask/'+side,{method:'POST',body:JSON.stringify({text})});
  const j=await res.json();clearInterval(tick);
  if(j.error){m.textContent='error';r.textContent=j.error;r.className='err';return}
  m.textContent='✅ '+j.seconds.toFixed(1)+'s';r.className='';r.textContent=j.text;
  t.innerHTML=j.tools.map(x=>'<code>🔧 '+x+'</code>').join('');
 }catch(e){clearInterval(tick);m.textContent='error';r.textContent=e;r.className='err'}
}
f.onsubmit=async e=>{e.preventDefault();if(!q.value.trim())return;b.disabled=true;
 await Promise.all([ask('local',q.value),ask('eks',q.value)]);b.disabled=false};
</script></body></html>"""


def ask_agent(base_url: str, text: str) -> dict:
    payload = {
        "jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send",
        "params": {"message": {"role": "user", "messageId": str(uuid.uuid4()),
                               "parts": [{"kind": "text", "text": text}]}},
    }
    req = urllib.request.Request(base_url + AGENT_PATH,
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = json.load(resp)
    result = body.get("result", {})
    parts = [p.get("text", "") for a in result.get("artifacts", [])
             for p in a.get("parts", []) if p.get("kind") == "text"]
    tools = [p["data"]["name"] for msg in result.get("history", [])
             for p in msg.get("parts", [])
             if p.get("kind") == "data"
             and (p.get("metadata") or {}).get("kagent_type") == "function_call"
             and p.get("data", {}).get("name")]
    return {"text": "\n".join(parts) or "(sin texto en la respuesta)",
            "tools": tools, "seconds": time.time() - t0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silencio
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(200, HTML, "text/html; charset=utf-8")

    def do_POST(self):
        side = self.path.rsplit("/", 1)[-1]
        if side not in SIDES:
            self._send(404, json.dumps({"error": "lado desconocido"}))
            return
        length = int(self.headers.get("Content-Length", 0))
        text = json.loads(self.rfile.read(length)).get("text", "")
        try:
            self._send(200, json.dumps(ask_agent(SIDES[side], text)))
        except Exception as e:  # port-forward caído, timeout, etc.
            self._send(200, json.dumps({"error": f"{type(e).__name__}: {e}"}))


if __name__ == "__main__":
    port = int(os.environ.get("PANEL_PORT", "7777"))
    print(f"panel: http://localhost:{port}  (local={SIDES['local']}  eks={SIDES['eks']})")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
