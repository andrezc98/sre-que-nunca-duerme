# infra-eks — camino cloud (OpenTofu)

Provisiona un EKS mínimo + IAM para que los agentes llamen a **Amazon Bedrock**.
Es el **camino grabado / producción**. La capa de Kubernetes (observabilidad + IA)
es la MISMA que en local — aquí solo cambia dónde vive el cluster y el modelo.

> ⚠️ **Apply gated en cuenta AWS** — no ejecutar hasta tener credenciales.
> Además: **habilitar acceso al modelo Claude Sonnet 4.6** en la consola de Bedrock
> (ajuste de cuenta, no de Terraform).

## Qué provisiona
- VPC (3 AZ, 1 NAT) · EKS 1.33 (managed node group `t3.large` ×2)
- Addon `eks-pod-identity-agent` + rol IAM con `bedrock:InvokeModel*`
  (perfil de inferencia `us.anthropic.claude-sonnet-4-6` + foundation-model)
- Pod Identity para el SA `kagent` y el operator K8sGPT

## Uso
```bash
cd infra-eks
tofu init
tofu apply                                  # VPC + EKS + IAM Bedrock
aws eks update-kubeconfig --name kcd-demo --region us-east-1

# luego, la MISMA capa que en local:
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.4.4/manifests/install.yaml
kubectl apply -f ../gitops/root.yaml
kubectl apply -f ../ai/kagent/
../demo/swap-brain.sh bedrock-claude
```

## Con Pod Identity: sin llaves estáticas
Bedrock recibe las credenciales por Pod Identity, así que en EKS **quita
`apiKeySecret`** de `../ai/kagent/modelconfig-bedrock.yaml` (el SDK toma el rol
del pod). Igual para K8sGPT: usa `../ai/k8sgpt/k8sgpt-bedrock.yaml` sin `secret`.
