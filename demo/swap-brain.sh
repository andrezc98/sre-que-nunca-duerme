#!/usr/bin/env bash
# El clímax: cambia el "cerebro" del agente sin tocar nada más.
#   ./swap-brain.sh ollama-qwen      -> modelo local, $0
#   ./swap-brain.sh bedrock-claude   -> Claude Sonnet 4.6 en Bedrock
#   ./swap-brain.sh bedrock-sonnet-5 -> Claude Sonnet 5 en Bedrock
#   ./swap-brain.sh bedrock-opus     -> Claude Opus 4.8 en Bedrock
# (GPT-5.6 en Bedrock quedo fuera: solo se sirve por la Responses API del
#  endpoint Mantle y el provider OpenAI de kagent habla Chat Completions.)
set -euo pipefail
MODEL="${1:-}"
case "$MODEL" in
  ollama-qwen|qwen36-27b|bedrock-claude|bedrock-sonnet-5|bedrock-opus) ;;
  *) echo "Uso: $0 <ollama-qwen|qwen36-27b|bedrock-claude|bedrock-sonnet-5|bedrock-opus>"; exit 1 ;;
esac

kubectl -n kagent patch agent sre-agent --type merge \
  -p "{\"spec\":{\"declarative\":{\"modelConfig\":\"$MODEL\"}}}"

echo "Cerebro del agente -> $MODEL   (mismo Agent, un solo campo)"
