# Resultados del test end-to-end (kind local) — 2026-07-14

Salidas reales de la primera corrida completa del camino local, para comparar
durante los ensayos. Cluster: kind v0.32 (K8s v1.36.1) sobre OrbStack, macOS.
Modelo local: qwen3.5:4b (3.4 GB) vía Ollama (100% GPU Metal).

## 1. K8sGPT CLI — "los ojos" (momento hero en vivo)

Tras `./demo/break-pod.sh` (pod `roto`, imagen `nginx:noexiste`):

```
k8sgpt analyze --explain --filter Pod --namespace default --language spanish
```

Respuesta (~segundos, modelo ya caliente):

> **0: Pod default/roto()**
> Error: La imagen no existe en Docker Hub por nombre o etiqueta inválida
> ("nginx:noexiste"). Falló al intentar descargarla para iniciar el contenedor.
> Solution: 1. Verifica ortografía del tag, usa "nginx:latest". 2. Corrige
> imagen a "nginx" o usa tag oficial. 3. Usa kubectl apply -f y revisa logs.

Sin `--filter Pod`: ~11 hallazgos (ConfigMaps sin usar, ruido) × llamada LLM
cada uno = minutos. Con filtro: 1 llamada. **Usar siempre el filtro en vivo.**

## 2. Agente kagent — "las manos" (diagnóstico)

```
kagent invoke --agent sre-agent --task "¿Por qué falla el pod 'roto' en el
namespace default? Diagnostica y propone una solución."
```

Loop real del agente (trace A2A):

| Paso | Tool call | Resultado |
|---|---|---|
| 1 | `k8s_get_resources` (deployment/roto) | Error — supuso mal el tipo |
| 2 | `k8s_get_resources` (pods) — se autocorrigió | Vio `roto 0/1 ImagePullBackOff` |
| 3 | `k8s_get_pod_logs` (roto) | Error — no hay logs de imagen nunca descargada |
| 4 | Respuesta final | Diagnóstico ImagePullBackOff + causas + solución |

Y terminó **preguntando al humano** (¿tag exacto?, ¿registro privado?) en vez
de actuar: el guardrail "NUNCA ejecutes acciones destructivas sin aprobación
humana" del systemMessage, funcionando. Narrar el loop en el escenario: no es
un script, es un agente que se equivoca y se corrige.

## 3. Agente kagent — Prometheus vía MCP

```
kagent invoke --agent sre-agent --task "¿Qué dice Prometheus del uso de CPU
por pod en el namespace kagent? Usa prometheus_query_tool y resume en una
tabla corta."
```

El agente escribió su propio PromQL:

```promql
sum(rate(container_cpu_usage_seconds_total{namespace="kagent",container!=""}[5m])) by (pod_name, namespace)
```

consultó el Prometheus vivo (`kube-prometheus-stack-prometheus.monitoring:9090`),
recibió `0.0141 cores` reales y respondió en español con tabla + sugerencia de
comparar contra los requests. Estado A2A: `completed`.

## 4. Swap de cerebro (el clímax) — precondición

`./demo/swap-brain.sh bedrock-claude` SIN el secret `bedrock-credentials`:
- Agent queda `Accepted=False` ("Secret not found") pero el deployment viejo
  (Ollama) sigue sirviendo. Falla limpio, sin caída.
- `./demo/swap-brain.sh ollama-qwen` recupera `Accepted=True` al instante.
- **Crear el secret ANTES del swap en vivo** o el clímax no hace nada visible.

## Gotchas descubiertas (ya horneadas en README/manifests)

1. kind ≥ 0.32: kindnetd TRAE enforcement de NetworkPolicy (nfqueue). Las
   netpols stock de Argo CD le hacen blackhole a su propio DNS pod-a-pod
   (apps en Unknown por horas). Fix: `kubectl -n argocd delete netpol --all`.
2. k8sgpt CLI: `--baseurl http://localhost:11434` SIN `/v1` (API nativa).
   El operator es al revés: CRD sin backend `ollama` → `localai` CON `/v1`.
3. `KAGENT_DEFAULT_MODEL_PROVIDER=ollama` obligatorio para `kagent install`.
4. `kagent invoke` requiere `kubectl -n kagent port-forward svc/kagent-controller 8083:8083`.
5. Cluster raro tras dormir la laptop → `docker restart kcd-control-plane`.
