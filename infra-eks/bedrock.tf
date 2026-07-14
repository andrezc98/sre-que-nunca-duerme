# Acceso a Amazon Bedrock desde los pods vía EKS Pod Identity (AWS lo recomienda
# sobre IRSA). El agente Kagent (SA kagent) y el operator K8sGPT usan este rol,
# sin llaves estáticas.
#
# OJO: además del IAM hay que HABILITAR acceso al modelo Sonnet 4.6 en la consola
# de Bedrock (ajuste de cuenta, no de Terraform), o los invokes fallan igual.

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "pod_identity_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole", "sts:TagSession"] # TagSession es requerido por Pod Identity
    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }
  }
}

locals {
  account_id = data.aws_caller_identity.current.account_id

  # Claude en US solo es invocable vía perfil de inferencia cross-region (us.*).
  # Verifica las regiones destino reales antes de aplicar:
  #   aws bedrock get-inference-profile \
  #     --inference-profile-identifier us.anthropic.claude-sonnet-4-6 --region us-east-1
  bedrock_regions = ["us-east-1", "us-east-2", "us-west-2"]

  # El "menu de cerebros" para la demo (ModelConfigs en ai/kagent/).
  # GPT-5.6 en Bedrock quedó fuera del menú: solo se sirve vía Responses API
  # (namespace IAM bedrock-mantle:*, SigV4 soportado) y kagent habla Chat
  # Completions. Si algún día kagent/LiteLLM soportan ese path, agregar aquí
  # un statement bedrock-mantle:CreateInference.
  bedrock_claude_models = [
    "anthropic.claude-sonnet-4-6",
    "anthropic.claude-sonnet-5",
    "anthropic.claude-opus-4-8",
  ]
}

data "aws_iam_policy_document" "bedrock_invoke" {
  # Debes conceder invoke tanto al perfil de inferencia como al foundation-model
  # en cada región a la que enruta el perfil, o da AccessDeniedException.
  statement {
    sid     = "InferenceProfile"
    effect  = "Allow"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = flatten([for m in local.bedrock_claude_models : [
      for r in local.bedrock_regions :
      "arn:aws:bedrock:${r}:${local.account_id}:inference-profile/us.${m}"
    ]])
  }
  statement {
    sid     = "FoundationModel"
    effect  = "Allow"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = flatten([for m in local.bedrock_claude_models : [
      for r in local.bedrock_regions :
      "arn:aws:bedrock:${r}::foundation-model/${m}" # doble ':' (sin account)
    ]])
  }
}

# EBS CSI driver: mismo trust de Pod Identity, política administrada de AWS.
resource "aws_iam_role" "ebs_csi" {
  name               = "${var.cluster_name}-ebs-csi"
  assume_role_policy = data.aws_iam_policy_document.pod_identity_assume.json
}

resource "aws_iam_role_policy_attachment" "ebs_csi" {
  role       = aws_iam_role.ebs_csi.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

resource "aws_iam_role" "bedrock_agents" {
  name               = "${var.cluster_name}-bedrock-agents"
  assume_role_policy = data.aws_iam_policy_document.pod_identity_assume.json
}

resource "aws_iam_role_policy" "bedrock" {
  name   = "bedrock-invoke"
  role   = aws_iam_role.bedrock_agents.id
  policy = data.aws_iam_policy_document.bedrock_invoke.json
}

# Kagent: quien llama a Bedrock es el POD DEL AGENTE (no el controller), y su
# SA se llama como el Agent CR. Verificado en kind 2026-07-14: sre-agent.
# (Si agregas otro Agent con ModelConfig Bedrock, necesita su propia association.)
resource "aws_eks_pod_identity_association" "kagent" {
  cluster_name    = module.eks.cluster_name
  namespace       = "kagent"
  service_account = "sre-agent"
  role_arn        = aws_iam_role.bedrock_agents.arn
}

# K8sGPT: quien llama a Bedrock es el server pod que el operator crea desde el
# CR (no el manager). SA verificado en kind 2026-07-14 con el chart 0.2.27.
resource "aws_eks_pod_identity_association" "k8sgpt" {
  cluster_name    = module.eks.cluster_name
  namespace       = "k8sgpt-operator-system"
  service_account = "k8sgpt-k8sgpt-operator-system"
  role_arn        = aws_iam_role.bedrock_agents.arn
}
