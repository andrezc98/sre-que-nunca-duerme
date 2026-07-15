# El SRE que Nunca Duerme — Demo repo

Stack de observabilidad open source + agentes de IA sobre Kubernetes, para
**KCD Lima 2026** (18 jul 2026). Reproducible con un comando.

> El plan completo de la charla está en [`plan-kcd-lima-2026.md`](./plan-kcd-lima-2026.md).

## Qué construye

```
apps ─▶ OpenTelemetry ─▶ Prometheus 3 ─▶ Grafana 12   (observabilidad, todo CNCF)
                         Fluent Bit 4 ─▶ logs
                              │
                   K8sGPT (diagnostica) + Kagent (actúa vía MCP)
                              │
                  cerebro intercambiable:  Ollama/Qwen (local, $0)
                                        ↔  Claude/Bedrock (producción)
```

## Dos caminos

| | **Local (kind)** — camino principal de la demo en vivo | **Cloud (EKS)** — camino grabado / producción |
|---|---|---|
| Cluster | `kind` en tu laptop | EKS vía OpenTofu (`infra-eks/`) |
| Modelo | Ollama/Qwen local (offline, a prueba de WiFi) | Claude vía Bedrock + nodo GPU para Ollama |
| Cuándo | **demo en vivo en el escenario** | clip grabado ("así se ve en la nube") |
| Costo | $0 | EC2 + EKS + Bedrock |

La capa de Kubernetes (observabilidad + IA) es la **misma** en ambos — corre en
cualquier cluster. Solo cambia dónde vive el cluster y qué modelo usas.

## Prerequisitos

Ya instalado en esta máquina: `kubectl`, `docker`, `ollama`, `git`, `node`, `aws`, `terraform`.

Falta instalar (camino local):
```bash
brew install kind helm k8sgpt kagent   # cluster local, helm, CLIs de K8sGPT y Kagent
# opentofu (opcional, para el camino EKS): brew install opentofu
```

## Reproducir (camino local — probado en kind v0.32 / OrbStack, 2026-07-14)

```bash
# 1. Cluster local + modelo local
kind create cluster --name kcd
ollama pull qwen3.5:4b        # fija el tag EXACTO que pruebes

# 2. K8sGPT (los ojos) — CLI, el momento hero en vivo
# SIN /v1 en el baseurl: el backend ollama usa la API nativa (con /v1 -> 404).
k8sgpt auth add --backend ollama --model qwen3.5:4b --baseurl http://localhost:11434
k8sgpt auth default -p ollama
./demo/break-pod.sh
# --filter Pod = 1 sola llamada al LLM (sin filtro analiza ~11 hallazgos: lento en vivo)
k8sgpt analyze --explain --filter Pod --namespace default --language spanish

# 3. Kagent (las manos) — agente como CRD + swap de cerebro
KAGENT_DEFAULT_MODEL_PROVIDER=ollama kagent install --profile demo
kubectl apply -f ai/kagent/
kagent dashboard              # -> http://localhost:8082
# En el chat, pregunta p.ej.: "¿por qué falla el pod 'roto' y qué dice Prometheus
# del uso de CPU en el namespace default?"  (usa kubectl + Prometheus vía MCP)
./demo/swap-brain.sh bedrock-claude   # el clímax: un solo campo

# 4. Observabilidad + GitOps (Argo CD app-of-apps)
#    Requiere el repo en git: empújalo y pon tu repoURL en gitops/root.yaml.
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.4.4/manifests/install.yaml
# CRITICO en kind >= 0.32: kindnetd trae un enforcement de NetworkPolicy (nfqueue)
# que hace blackhole del trafico pod-a-pod de los pods de Argo CD (rompe su DNS,
# apps quedan en Unknown). En un cluster local de demo, borra las netpols:
kubectl -n argocd delete networkpolicies --all
kubectl apply -f gitops/root.yaml
kubectl apply -f ai/k8sgpt/k8sgpt-ollama.yaml   # tras el operator Synced
```

## Estructura

```
gitops/       Argo CD app-of-apps (observabilidad + IA)
ai/           manifests de K8sGPT y Kagent + el swap de modelo
demo/         scripts: romper pod, swap de cerebro
infra-eks/    OpenTofu para el camino cloud (opcional, grabado)
```

## Estado del build

- [x] README + estructura + CLAUDE.md
- [x] Scripts de demo (break-pod, swap-brain)
- [x] Kagent manifests v1alpha2 (Agent + ModelConfig Ollama/Bedrock + tools Prometheus)
- [x] Observabilidad + GitOps: Argo CD app-of-apps (kube-prometheus-stack, Alloy/OTel, Fluent Bit) + K8sGPT operator/CR (Ollama y Bedrock)
- [x] OpenTofu EKS + IAM Bedrock (Pod Identity) — *escrito; apply gated en cuenta AWS*
- [x] **Probado en kind local end-to-end** (2026-07-14): k8sgpt CLI+operator, agente
  kagent (kubectl + PromQL vía MCP), swap de cerebro, app-of-apps Argo CD.
- [x] **Probado en EKS end-to-end** (2026-07-14): EKS 1.36 (misma versión que kind),
  2× m9g.large Graviton5 + Bottlerocket, agente con Claude vía Bedrock (Pod
  Identity, cero API keys), PromQL en vivo, app-of-apps completo.
- [ ] Grabar el clip cloud + destruir (`tofu destroy`).

### Deltas EKS vs kind (aprendidos al probar)

1. `gp2` existe pero NO es StorageClass default → los PVC quedan Pending:
   `kubectl patch storageclass gp2 -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'`
2. Con Pod Identity, quitar `apiKeySecret` de los ModelConfigs Bedrock:
   `kubectl -n kagent patch modelconfig bedrock-claude --type json -p '[{"op":"remove","path":"/spec/apiKeySecret"}]'`
3. Primer paso tras instalar: `./demo/swap-brain.sh bedrock-claude` (no hay Ollama).
4. Las netpols de Argo CD NO rompen nada en EKS (VPC CNI no las aplica por
   defecto) — el fix de borrarlas es solo para kind >= 0.32.
