# El SRE que Nunca Duerme — Plan de charla
**KCD Lima, Perú 2026 · Sábado 18 de julio de 2026 · UTEC, Barranco**

> Plan de trabajo (en inglés para estructura, contenido de charla en español).
> Generado 2026-06-18. Las versiones y el estado de los proyectos están verificados a esta fecha — re-verificar versiones puntuales ~1 semana antes del evento.

---

## 0. Decisiones tomadas

| Decisión | Elección |
|---|---|
| Duración | **25 min + 5 Q&A** (confirmado — formato estándar de KCD Lima). Guion principal en §4; nota de expansión a 40–45 si cambiara. |
| Framing | **Production-gap** (el "7%") + ángulo de costo LATAM |
| Demos | **Híbrido**: live donde es seguro + clips grabados de respaldo + screencast completo como fallback total |
| Modelos en demo | **Ambos**: Ollama local (Qwen) ↔ Claude vía Bedrock — el "swap" es el clímax |
| Infra | EKS real + acceso a Claude (Bedrock) + nodo GPU en EKS (g5/g6) para Ollama |
| Idioma | Español (KCD Lima es Spanish-first) |
| Tono CNCF | Vendor-neutral, project-focused — sin pitch de producto |

---

## 1. Realidad del evento (verificado)

- **Fecha:** sábado 18 de julio de 2026 · 8:30–18:00 · UTEC, Barranco, Lima (~600 asistencias).
- **Formato estándar de talk:** 25 min + 5 Q&A. (Lightning 15, Panel 30+5, Workshop 120–180.) **Tienes slot de 40–45 → confirmar por escrito.**
- **Audiencia:** dev, DevOps/SRE, plataforma, estudiantes — seniority mixta, habrá principiantes.
- **Tracks que encajan:** AI/ML, Operations + Performance, Observability.
- **Regla CNCF que aplica:** sin pitch de producto. Bedrock/Anthropic se presentan como "backend intercambiable", nunca como recomendación comercial.

---

## 2. Qué cambió desde el CFP (refresh de exactitud)

Ordenado por riesgo de "esto suena viejo":

1. **OpenTelemetry se graduó en CNCF (21 may 2026).** Es EL riesgo de quedar desactualizado. Agregar un **OTel Collector o Grafana Alloy** como capa de pegamento que alimenta el stack. Prometheus 3 tiene receptor OTLP nativo; Fluent Bit 4.x habla OTLP y mueve logs+métricas+trazas.
2. **"AI explica errores" ya es table-stakes.** No es la revelación que era. Mencionar y diferenciar de **HolmesGPT** (Robusta + Microsoft, CNCF Sandbox desde oct 2025), **kubectl-ai** (Google), **Grafana Assistant** (NL→PromQL, GA). El framing 2026 que resuena: **~66% corre GenAI en K8s, solo ~7% en producción diaria** — los agentes están atascados en pilotos día-1.
3. **Suavizar el superlativo de Kagent.** "El framework de agentes más activo de CNCF" **no es defendible literalmente**. Usar: *"uno de los proyectos agénticos de más rápido crecimiento en CNCF Sandbox, donado por Solo.io (el equipo de Istio)"*. ~2,800 stars, 100+ contributors, salud CNCF 78.
4. **Kagent — cambios que romperían tu YAML viejo:** API ahora **`kagent.dev/v1alpha2`** (campos renombrados, `apiKeySecretRef`→`apiKeySecret`); corre sobre **ADK runtime, no AutoGen** (eliminar la línea de AutoGen); **kmcp se auto-instala**; **Bedrock es first-class** (con extended thinking + prompt caching); solo Postgres (SQLite eliminado). Nuevo y demostrable: **human-in-the-loop con aprobación, memoria de agente, Skills, runtime Go rápido, agentevals**.
5. **K8sGPT diagnostica, NO remedia.** No sobre-prometer "aplica soluciones". Es el mejor puente narrativo: **K8sGPT = los ojos** (explain, read-only), **Kagent = las manos** (actúa vía MCP, con guardrails HITL). Actual: v0.4.33, MCP server v2 es lo nuevo, 13+ backends incl. Bedrock + Anthropic nativo.
6. **El frontier honesto = tu credibilidad.** Gobernanza/identidad/authz de agentes es lo genuinamente sin resolver en 2026: MCP donado a Linux Foundation (dic 2025), **OWASP MCP Top 10**, identidad de agente con SPIFFE/SPIRE (kagenti), policy proxy (agentgateway). Decir "esta capa todavía no existe del todo" = señal de que estás al día.
7. **Versiones correctas:** Prometheus **3.x**, Argo CD **3.x**, Fluent Bit **4.x**, Grafana **12.x**, OpenTofu **1.12** (ha *divergido* de Terraform: state encryption, dynamic `prevent_destroy`, OCI registry; Terraform ahora es de IBM/BSL). No llamar a OpenTofu "solo un fork de Terraform".
8. **Modelos para la demo:** *Live offline* = **Qwen3.5 4B vía Ollama** (3.4 GB, ~97.5% tool-calling, corre en laptop). En el nodo GPU de EKS puedes correr algo mayor (Qwen3.6 27B). *Producción* = Claude en Bedrock: `anthropic.claude-sonnet-4-6` (balance costo/latencia) o `anthropic.claude-opus-4-8` (razonamiento más profundo). **Fijar el tag/ID exacto que pruebes.**

### Table-stakes vs diferenciación (no sobre-vender novedad)
- **Ya es básico (no presumir como nuevo):** LLM explica errores; MCP da herramientas al agente; agentes como CRDs; NL→PromQL.
- **Suena actual y creíble:** la brecha del 7% (día-2/producción), guardrails + HITL, gobernanza/identidad de agentes, costo-consciencia LATAM, demo real en español.

---

## 3. Arquitectura de referencia (lo que construyes)

```
                 OpenTofu (IaC)  ──aplica──▶  EKS
                       │                       │
                 Argo CD (GitOps) ◀── git ──   │  (app of apps)
                       │                       │
   ┌───────────────────┴───────────────────────────────────┐
   │  Observabilidad (CNCF, OSS)                              │
   │   apps ─▶ OTel Collector / Alloy ─▶ Prometheus 3 (OTLP) │
   │                                  └─▶ Loki (logs)         │
   │   Fluent Bit 4 (node forwarder, OTLP) ──────────────────┤
   │   Grafana 12 (dashboards/alertas)                        │
   └───────────────────┬─────────────────────────────────────┘
                        │  scrape / consulta
   ┌────────────────────┴────────────────────────────────────┐
   │  Capa de IA                                               │
   │   K8sGPT (ojos): analyze --explain  +  operator (CRs)     │
   │        └─ MCP server v2 (k8sgpt serve --mcp)              │
   │   Kagent (manos): Agent CRD (v1alpha2) + MCP tools        │
   │        ├─ tools MCP: kubectl, Prometheus, Argo CD, Grafana│
   │        └─ ModelConfig ──┬─ Ollama (Qwen) en nodo GPU       │
   │                         └─ AmazonBedrock (Claude)          │
   └───────────────────────────────────────────────────────────┘
```

**Nodo GPU para Ollama:** node group GPU en EKS (`g5.xlarge` A10G o `g6` L4). Taints + nodeSelector para que solo Ollama caiga ahí. Alternativa más barata para el día del evento: correr Qwen3.5 4B **en tu laptop** (offline, determinista) y usar Bedrock para la rama "producción".

---

## 4. Estructura narrativa — guion 25 min (+5 Q&A)

Spine = production-gap. **Regla de oro a 25 min con demos: una sola demo en vivo (la hero), el resto en clips grabados.** El tiempo es el enemigo; protege el Acto 2.

**Presupuesto de tiempo:**
| Bloque | Min |
|---|---|
| Hook | 2 |
| Acto 1 — stack abierto | 3 |
| Acto 2 — el cerebro (corazón) | 12 |
| Acto 3 — día-2 honesto | 5 |
| Cierre + QR | 2 |
| *(Q&A aparte)* | *5* |

### Hook — 2 min
- "~66% corre GenAI en K8s, pero solo ~7% lo opera en producción — los agentes están atascados en pilotos."
- Ángulo LATAM: "y pagamos SaaS de observabilidad carísimo sin saber que el stack OSS ya es production-ready."
- Tesis: **constrúyelo abierto, dale un cerebro, y mantenlo con correa.**

### Acto 1 — El stack abierto — 3 min
- Por qué OSS + CNCF: portable, reproducible, sin lock-in. OpenTofu (IaC) + Argo CD (GitOps).
- El stack: Prometheus 3 + Grafana 12 + Fluent Bit 4, **con OTel Collector/Alloy como pegamento** (esto te mantiene actual).
- **Build pre-horneado — NO `tofu apply` en vivo** (no hay tiempo). Mostrar Argo CD ya verde + un dashboard de Grafana. Mensaje: "gratis, reproducible, lo replicas hoy."

### Acto 2 — Dale un cerebro — 12 min (el corazón, no recortar)
- **K8sGPT (los ojos) — [LIVE, la única demo en vivo]:**
  - `kubectl run roto --image=nginx:noexiste` → `k8sgpt analyze --explain` → diagnóstico humano en español.
  - Mencionar: 13+ backends, MCP server v2. **Aclarar: diagnostica, NO remedia.**
- **Kagent (las manos) — [REC clip]:**
  - Agentes como CRDs nativos (`kagent.dev/v1alpha2`), tools vía MCP (kubectl, Prometheus, Argo CD), donado por Solo.io. El agente consulta Prometheus + kubectl y propone una acción. (Live aquí = demasiado riesgo de tiempo.)
- **El clímax — swap del cerebro — [REC clip]:**
  - `ModelConfig`: `provider: Ollama` (Qwen local) → `provider: AmazonBedrock` (`anthropic.claude-sonnet-4-6`). **Mismo Agent CRD, un solo campo.**
  - Punchline de costo: Qwen local = $0 · Sonnet 4.6 = $3/$15 por M tokens · Opus 4.8 = $5/$25. "Mismo agente, tú eliges la cuenta."

### Acto 3 — Día 2: la parte honesta — 5 min (tu diferenciador)
- Lo que **no** hace: K8sGPT no remedia solo; remediación autónoma sigue aspiracional.
- **Guardrails:** human-in-the-loop de Kagent (aprobación de tools), RBAC mínimo, read-only por defecto.
- **Frontier sin resolver:** identidad/authz de agentes — MCP→Linux Foundation, OWASP MCP Top 10, SPIFFE/SPIRE (kagenti), agentgateway. "El SRE que nunca duerme todavía necesita supervisión."
- Diferenciación honesta vs HolmesGPT / kubectl-ai / Grafana Assistant — **una frase**, no más.

### Cierre — 2 min
- Repo público "replícalo hoy" + QR. Mensaje: abierto, portable, sin lock-in; el modelo es intercambiable, el stack no cambia.

**Si consiguieras 40–45 min:** expande Acto 1 a build en vivo (`tofu apply` + Argo sync), pasa la demo de Kagent y el swap a vivo (con clip de respaldo), y profundiza el frontier del Acto 3. **[FALLBACK]** siempre: un screencast completo narrado por si muere el cluster.

---

## 5. Plan de demos (híbrido) + comandos

| Momento | Estrategia | Comando / acción | Respaldo |
|---|---|---|---|
| Build IaC/GitOps | [LIVE] o [REC] | `tofu apply`; Argo CD sync | screencast |
| K8sGPT diagnóstico | **[LIVE]** (hero) | `kubectl run roto --image=nginx:noexiste` → `k8sgpt analyze --explain` | clip grabado |
| K8sGPT CrashLoop | [LIVE] opcional | pod que crashea → `k8sgpt analyze --explain --with-doc` | clip |
| Kagent agente | [LIVE o REC] | dashboard :8082 → prompt NL → MCP a Prometheus/kubectl | video |
| **Swap de modelo** | **[LIVE]** | editar `ModelConfig` Ollama→Bedrock, re-aplicar | clip con Claude |
| Fallback total | [FALLBACK] | screencast completo de 6–8 min narrado en vivo | — |

**Comandos de referencia (verificar versión el día previo):**
```bash
# K8sGPT CLI
brew install k8sgpt
k8sgpt auth add --backend amazonbedrock --model anthropic.claude-sonnet-4-6 --providerRegion us-east-1
# (local) k8sgpt auth add --backend localai/ollama  → endpoint http://<gpu-node>:11434
k8sgpt analyze --explain

# K8sGPT operator (escaneo continuo)
helm repo add k8sgpt https://charts.k8sgpt.ai/
helm install release k8sgpt/k8sgpt-operator -n k8sgpt-operator-system --create-namespace
kubectl get results -A

# Kagent
brew install kagent           # o curl install
kagent install --profile demo # kind/EKS + helm
kagent dashboard              # → http://localhost:8082

# Ollama (nodo GPU o laptop) — fijar el tag exacto
ollama pull qwen3.5:4b        # demo laptop, ~3.4GB, ~97.5% tool-calling
# (GPU) ollama pull qwen3.6:27b
```

**ModelConfig — el swap (esquema v1alpha2, validar campos contra docs el día previo):**
```yaml
# Local (Ollama) — ai/kagent/modelconfig-ollama.yaml
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata: { name: ollama-qwen, namespace: kagent }
spec:
  provider: Ollama
  model: qwen3.5:4b
  ollama: { host: http://host.docker.internal:11434 }
---
# Producción (Bedrock) — el swap es un campo en el Agent, no aquí
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata: { name: bedrock-claude, namespace: kagent }
spec:
  provider: Bedrock                       # enum exacto (NO "AmazonBedrock")
  model: us.anthropic.claude-sonnet-4-6   # perfil de inferencia US (el id base falla en US)
  apiKeySecret: bedrock-credentials       # renombrado en v1alpha2; omitir con IRSA
  bedrock: { region: us-east-1 }
```

---

## 6. Descripción/abstract refrescado (para intro y notas, no para re-enviar)

> Cuando conectas un LLM a tu stack de observabilidad, el dashboard deja de ser algo que tú revisas y se vuelve un agente que diagnostica y propone. En esta charla armo el stack completo y abierto — Prometheus 3, Grafana 12, Fluent Bit 4 con OpenTelemetry como capa estándar, desplegado en Kubernetes con OpenTofu (IaC) y Argo CD (GitOps), todo CNCF. Encima conecto dos proyectos CNCF Sandbox: **K8sGPT**, que escanea el cluster y explica errores en lenguaje humano, y **Kagent** (donado por Solo.io), que define agentes como recursos nativos de Kubernetes con acceso a Prometheus, Argo CD y kubectl vía MCP. El modelo es intercambiable: Ollama con Qwen para experimentar sin costo, o Claude vía Bedrock/Anthropic cuando necesitas razonamiento profundo en producción — un cambio de un campo. Pero el valor real está en cruzar la brecha entre el piloto y producción: guardrails, human-in-the-loop, y la frontera abierta de identidad y autorización de agentes.

(Quita "el framework más activo", quita "aplica soluciones" para K8sGPT, agrega OTel y la parte honesta de día-2.)

---

## 7. Checklist día del evento (anti-WiFi)
- [ ] Cluster EKS desplegado y verificado la noche anterior; snapshot/estado guardado.
- [ ] Modelo local Qwen3.5 4B descargado **en la laptop** (offline) — no depender de la red para el hero demo.
- [ ] Credenciales Bedrock probadas; región correcta; cuota verificada.
- [ ] Todos los clips grabados (K8sGPT, Kagent, swap) + 1 screencast completo de respaldo.
- [ ] Versiones fijadas y reconfirmadas (~1 semana antes): K8sGPT, Kagent (v1alpha2), Ollama tag, IDs Bedrock.
- [ ] Slides exportadas a PDF (sin dependencia de internet).
- [ ] QR del repo probado.
- [ ] Cluster de respaldo local (kind) por si EKS no responde.

---

## 8. Cronograma de preparación (hoy 18 jun → 18 jul, ~4 semanas)

| Semana | Foco |
|---|---|
| **1 (jun 18–24)** | Construir el repo: OpenTofu + EKS + Argo CD + stack OSS + OTel. Validar K8sGPT CLI/operator. Validar Kagent install + dashboard + un agente con MCP. |
| **2 (jun 25–jul 1)** | El swap Ollama↔Bedrock funcionando end-to-end. Nodo GPU o decisión laptop. Grabar primeros clips. Fijar versiones. |
| **3 (jul 2–8)** | Slides + guion cronometrado. Ensayo completo con timer (40–45 y versión 25). Grabar clips finales + screencast de respaldo. |
| **4 (jul 9–17)** | Ensayos repetidos, recortar a tiempo, re-verificar versiones, publicar repo, preparar QR. Buffer para imprevistos. |

---

## 9. Esqueleto de slides

Para **25 min apunta a ~12–14 slides** (fusiona 5–8 en una de "por qué OSS/CNCF + OTel"; combina 16–19 en dos de día-2). Lista base (recorta para 25):
1. Título + quién eres
2. El gancho del 7% (gráfico)
3. Ángulo LATAM (costo SaaS vs OSS)
4. Tesis: construir / cerebro / correa
5. Por qué CNCF + OSS (sin lock-in)
6. OpenTofu + Argo CD (IaC + GitOps)
7. El stack: Prometheus 3 / Grafana 12 / Fluent Bit 4
8. **OTel como capa estándar (Collector/Alloy)** ← actualidad
9. [DEMO 1] build + Argo sync
10. K8sGPT: los ojos (qué es, 13+ backends, MCP v2)
11. [DEMO 2] k8sgpt analyze --explain (live)
12. Kagent: las manos (CRDs v1alpha2, MCP, Solo.io)
13. [DEMO 3] agente consultando Prometheus/kubectl
14. El cerebro intercambiable (Ollama ↔ Claude/Bedrock)
15. [DEMO 4] el swap + tabla de costos
16. Día 2: lo que NO hace (no remedia solo)
17. Guardrails + human-in-the-loop
18. Frontier: identidad/authz de agentes (MCP→LF, OWASP MCP Top 10, SPIFFE)
19. Diferenciación honesta (HolmesGPT / kubectl-ai / Grafana Assistant)
20. Cierre: replícalo hoy (QR) + mensaje sin lock-in
21. Gracias / Q&A

---

## 10. Apéndice — fact-check (jun 2026)
- KCD Lima: kcdlima.pe · community.cncf.io/kcd-lima-peru · sessionize.com/kcd-lima-peru-2026 — 18 jul 2026, UTEC Barranco, talks 25+5, Spanish-first.
- OpenTelemetry graduado CNCF: 21 may 2026.
- Kagent: CNCF Sandbox (acept. 22 may 2025), donado por Solo.io, API v1alpha2, ADK runtime, ~v0.9.9 (17 jun 2026), kmcp auto-install. NO "incubating", NO "más activo" literal, NO AutoGen.
- K8sGPT: CNCF Sandbox, v0.4.33 (may 2026), MCP server v2 (v0.4.27), 13+ backends incl. Bedrock + Anthropic nativo. Diagnostica, no remedia.
- Versiones: Prometheus 3.x, Argo CD 3.x, Fluent Bit 4.x, Grafana 12.x, OpenTofu 1.12.
- Modelos: Qwen3.5 4B (demo local, 97.5% tool-calling); Bedrock Claude vía **perfil de inferencia US**: `us.anthropic.claude-sonnet-4-6` / `us.anthropic.claude-opus-4-8` (el id base sin prefijo `us.` falla en regiones US). Pricing (1ª parte): Sonnet $3/$15, Opus $5/$25, Haiku $1/$5 por M tokens.
- Competencia a name-check: HolmesGPT (Robusta+MS, Sandbox oct 2025), kubectl-ai (Google), Grafana Assistant (NL→PromQL GA).
- Frontier: MCP→Linux Foundation (dic 2025), OWASP MCP Top 10, kagenti (SPIFFE/SPIRE), agentgateway.
