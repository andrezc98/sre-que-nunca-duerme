# Guía de pegado — template oficial Google Slides KCD Lima 2026

> Fuente de verdad: `deck.md` (Marp; ahí están las speaker notes completas).
> Layouts del template: **L1** título arriba-izq fondo claro · **L2** blob azul izquierda + título centrado (divider) · **L3** fondo azul + lista numerada · **L4** panel azul izquierda con statement (≤4 líneas) · **L5** onda (portada/cierre).

Historia: **una noche, hora por hora — todo pasa ESA noche**. 7:04 p.m. terminaste por hoy → números de lo que está en juego → la escena ya estaba montada → **7:31 p.m. suena el celular (ni llegaste a la cena)** → 7:33 el diagnóstico llegó solo → 7:40 el agente investiga → ¿cuánto modelo necesitas? (benchmark) → 1:58 a.m. el fix está listo, ¿lo dejas aplicarlo solo? → **demo en vivo como cierre** → **2:47 a.m. fix aprobado, a dormir** → fuentes proyectadas en Q&A.

| # | Layout | Texto grande | Apoyo / extra | Imagen |
|---|--------|--------------|----------------|--------|
| 1 | L5 | El SRE que nunca duerme | subtítulo + nombre + rol | — |
| 2 | L4 | **7:04 p.m.** | "Cierras la laptop. Terminaste por hoy." | — |
| 3 | L4 | **$15,000** | "se pierden por CADA minuto caído" · Splunk/Oxford 2026 | — |
| 4 | L4 | **34%** | "de tu semana es toil: chamba manual que no construye nada" · 25→30→34 | — |
| 5 | L4 | **7%** | "solo 7 de cada 100 con GenAI la despliegan a diario" · 82/66 de contexto | — |
| 6 | L4 | **$65,000,000** | "UNA empresa, UN año, solo por MIRAR sus sistemas" · final: migró a Prometheus+Grafana | — |
| 7 | L3 | Esta charla es esa noche: 7 p.m. → 3 a.m. | 1 stack open source · 2 cerebro · 3 control humano | — |
| 8 | L1 | El elenco de esta noche | tabla 10 filas "qué hace, en cristiano" | logos pequeños |
| 9 | L1 | La escena ya estaba montada — desde hace semanas | dos comandos · $0 licencias · replicable | 📸 SS Argo CD en verde |
| 10 | L4 | **7:31 p.m.** | "Suena el celular. Ni llegaste a la cena." | 🐶 MEME *This is fine* |
| 11 | L1 | Los ojos ya estaban abiertos | K8sGPT · proyecto CNCF (la fundación de K8s) · **diagnostica, no aplica** | logo |
| 12 | L1 | 7:33 p.m. — el diagnóstico llegó solo | "la imagen no existe; así se arregla" | 📸 SS salida k8sgpt en español |
| 13 | L1 | 7:40 p.m. — alguien tiene que investigar. No tienes que ser tú. | kagent · YAML · MCP · Solo.io (equipo de Istio) | logo |
| 14 | L1 | El agente investiga solo | pregunta en español → causa + propuesta | 📸 SS del panel (localhost:7777) |
| 15 | L1 | En una esquina: los open source. En la otra: los propietarios. | swap = 1 campo YAML · "solo cambia quién piensa" | 🧠 MEME *expanding brain* |
| 16 | L2 | ¿Cuánto modelo necesita un SRE? | 6 incidentes × 7 modelos = 42 diagnósticos | — |
| 17 | L1 | Acertar ya cuesta centavos | screenshot con números aprobados | 📊 `assets/report-tiles.png` |
| 18 | L4 | **13.2 pasos · 39,000 tokens** | "MiniMax llegó. Nadie sabe cómo." | 🕵️ MEME *Pepe Silvia* |
| 19 | L1 | ¿Qué le pasó a MiniMax? | pagas precio × pasos · 39k vs ~5k tokens | — |
| 20 | L1 | La lección: no llames al SOTA para cada incidente | Epoch 3–4 meses · 9/13 Pareto · ½–⅙ precio · 10×/año | — |
| 21 | L1 | ¿Entonces la IA ya resolvió el on-call? No. | IBM: ~1 de cada 8 · frontier: menos de la mitad · lo mío = fallos de manual | — |
| 22 | L3 | 1:58 a.m. — el fix está listo. ¿Lo dejamos aplicarlo solo? Todavía no. | promesa≠producto · Gartner >40% cancelados · humano aprueba | — |
| 23 | L1 | Tres preguntas que hoy nadie puede responder | ¿quién es? ¿qué toca? ¿quién audita? + quiénes trabajan en ello | — |
| 24 | L2 | [DEMO EN VIVO] No me crean nada: rompámoslo juntos | los 2 comandos · offline, a prueba de WiFi | terminal en vivo |
| 25 | L1 | 2:47 a.m. — fix aprobado, cluster en verde. Ahora sí: a dormir. | repo: 2 rutas + benchmark + guion + fuentes · "una tarde" | QR grande |
| 26 | L5 | Gracias · ¿Preguntas? | — | — |
| 27 | L1 | Fuentes | lista con hipervínculos (queda proyectada en Q&A) | — |

## Memes (3)
- **S10** This is fine — el celular a las 3:07.
- **S15** Expanding brain (Qwen 4B → GLM/Kimi → Sonnet → Opus) — abre la pelea OSS vs propietario.
- **S18** Pepe Silvia — MiniMax caótico; el cliffhanger se resuelve en S19.

## Assets
- [x] Screenshot del report: `assets/report-tiles.png` (S17) y `assets/report-full.png` (backup swimlanes). Números aprobados 2026-07-15.
- [ ] 📸 SS Argo CD en verde (S9)
- [ ] 📸 SS salida k8sgpt en español (S12)
- [ ] 📸 SS panel del agente (S14)
- [ ] QR del repo (S25).
- [ ] Clip de respaldo de la demo en vivo (S24) — por si el cluster local falla.

## Cómo sacar cada pantallazo (cluster kind, todo local)

Antes de todo: cluster arriba (`docker restart kcd-control-plane` si la laptop durmió) y contexto correcto (`kubectl config use-context kind-kcd`).

**S9 — Argo CD en verde** (⚠️ SIEMPRE con `--context`: sin él apunta al cluster del contexto activo — así se envenenó el benchmark):
```bash
kubectl --context kind-kcd -n argocd port-forward svc/argocd-server 8080:443
# password: kubectl --context kind-kcd -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```
→ abre https://localhost:8080 (usuario `admin`), vista **Applications** con todo Healthy/Synced. Pantalla completa, zoom cómodo.

**S12 — K8sGPT en español (terminal):**
```bash
./demo/break-pod.sh
k8sgpt analyze --explain --filter Pod --namespace default --language spanish
```
→ SS del terminal con el diagnóstico. La salida esperada está en `demo/resultados-2026-07-14.md` (sección 1) por si quieres comparar. Tip: agranda la fuente del terminal (⌘+) antes del SS — en proyector se lee desde atrás.

**S14 — Panel del agente:**
```bash
kubectl --context kind-kcd -n kagent port-forward svc/kagent-controller 8083:8083
kubectl --context eks-demo  -n kagent port-forward svc/kagent-controller 8084:8083   # opcional, si EKS sigue vivo
python3 demo/panel.py
```
→ abre localhost:7777, pregunta "¿Por qué falla el pod roto y qué dice Prometheus del CPU?" y SS con pregunta + respuesta + herramientas usadas. Alternativa: `kagent dashboard` (localhost:8082) si prefieres la UI oficial.

**Tip general:** mismo tema oscuro y mismo zoom en los tres SS para que se vean de la misma familia.
