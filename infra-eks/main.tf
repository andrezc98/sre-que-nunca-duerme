# EKS mínimo para el camino cloud/grabado. La capa de Kubernetes (gitops/ + ai/)
# es la MISMA que en local: aquí solo se provisiona el cluster + IAM para Bedrock.
# Corre en una VPC EXISTENTE (var.vpc_id) reutilizando su IGW; lo único de red
# que se crea son 2 subnets desde un CIDR secundario + 1 route table (gratis).

# La VPC destino solo tiene subnets en Local Zone (us-east-1-lim-1a) y una /27:
# EKS exige >=2 AZs ESTÁNDAR, así que estas subnets son obligatorias, no gusto.
resource "aws_subnet" "demo" {
  for_each                = var.public_subnets
  vpc_id                  = var.vpc_id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true # egreso directo vía IGW (la VPC no tiene NAT)
}

data "aws_internet_gateway" "existing" {
  filter {
    name   = "attachment.vpc-id"
    values = [var.vpc_id]
  }
}

# Route table propia: no tocar las route tables del dueño de la VPC.
resource "aws_route_table" "demo" {
  vpc_id = var.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.existing.internet_gateway_id
  }
}

resource "aws_route_table_association" "demo" {
  for_each       = aws_subnet.demo
  subnet_id      = each.value.id
  route_table_id = aws_route_table.demo.id
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  endpoint_public_access                   = true  # alcanzable desde la laptop (default: false)
  authentication_mode                      = "API" # access entries (v21 quitó aws-auth)
  enable_cluster_creator_admin_permissions = true  # sin esto NO tienes admin del cluster (default: false)

  addons = {
    coredns                = {}
    kube-proxy             = {}
    vpc-cni                = { before_compute = true }
    eks-pod-identity-agent = { before_compute = true } # requerido para Pod Identity (Bedrock + EBS CSI)
    # Sin esto NINGÚN PVC liga en EKS 1.33 (no hay provisioner in-tree) y
    # kagent-postgresql queda Pending. En kind lo regala local-path-provisioner.
    aws-ebs-csi-driver = {
      pod_identity_association = [{
        role_arn        = aws_iam_role.ebs_csi.arn
        service_account = "ebs-csi-controller-sa"
      }]
    }
  }

  vpc_id                   = var.vpc_id
  subnet_ids               = [for s in aws_subnet.demo : s.id]
  control_plane_subnet_ids = [for s in aws_subnet.demo : s.id]

  eks_managed_node_groups = {
    default = {
      # Graviton5 + Bottlerocket (OS minimalista para contenedores: boot rápido,
      # superficie de ataque chica — buen material de charla). Todo el stack ya
      # corrió en arm64 (kind sobre Apple Silicon), así que ARM es riesgo cero.
      # m9g = GA jun 2026; si el MNG no lo acepta o no hay capacidad, volver a
      # ["m8g.large"] (probado). Evita *.medium: en EKS con VPC CNI los medium
      # Graviton topan ~8 pods/nodo y el stack trae ~45.
      instance_types = ["m9g.large"]
      ami_type       = "BOTTLEROCKET_ARM_64"
      min_size       = 2
      max_size       = 3
      desired_size   = 2 # honrado solo al crear; el módulo lo ignora en applies posteriores
    }
  }
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "configure_kubectl" {
  description = "Tras 'tofu apply', conecta kubectl:"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}"
}
