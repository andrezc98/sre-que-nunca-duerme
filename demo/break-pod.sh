#!/usr/bin/env bash
# Rompe un pod a propósito para la demo hero: imagen inexistente -> ImagePullBackOff.
# Luego K8sGPT lo diagnostica en lenguaje humano. Idempotente: re-ejecutable.
set -euo pipefail
NS="${1:-default}"

echo "Creando pod roto (imagen inexistente) en namespace '$NS'..."
kubectl -n "$NS" delete pod roto --ignore-not-found
kubectl -n "$NS" run roto --image=nginx:noexiste

echo
echo "Espera ~10s, luego:   k8sgpt analyze --explain"
echo "Limpiar:              kubectl -n $NS delete pod roto"
