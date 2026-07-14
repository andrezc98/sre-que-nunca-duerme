#!/usr/bin/env bash
# El clímax: cambia el "cerebro" del agente sin tocar nada más.
#   ./swap-brain.sh ollama-qwen     -> modelo local, $0
#   ./swap-brain.sh bedrock-claude  -> Claude en Bedrock, razonamiento profundo
set -euo pipefail
MODEL="${1:-}"
case "$MODEL" in
  ollama-qwen|bedrock-claude) ;;
  *) echo "Uso: $0 <ollama-qwen|bedrock-claude>"; exit 1 ;;
esac

kubectl -n kagent patch agent sre-agent --type merge \
  -p "{\"spec\":{\"declarative\":{\"modelConfig\":\"$MODEL\"}}}"

echo "Cerebro del agente -> $MODEL   (mismo Agent, un solo campo)"
