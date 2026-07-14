# EKS mínimo para el camino cloud/grabado. La capa de Kubernetes (gitops/ + ai/)
# es la MISMA que en local: aquí solo se provisiona el cluster + IAM para Bedrock.
# Módulos oficiales (ponytail: no hacer VPC/EKS a mano).

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  cidr = "10.0.0.0/16"
  azs  = slice(data.aws_availability_zones.available.names, 0, 3)
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = var.cluster_name
  cidr = local.cidr
  azs  = local.azs

  private_subnets = [for k, v in local.azs : cidrsubnet(local.cidr, 4, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.cidr, 8, k + 48)]

  enable_nat_gateway   = true
  single_nat_gateway   = true # un solo NAT/EIP: mínimo costo y cuota
  enable_dns_hostnames = true

  public_subnet_tags  = { "kubernetes.io/role/elb" = 1 }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }

  tags = { Environment = "demo" }
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

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      # Graviton4 + Bottlerocket (OS minimalista para contenedores: boot rápido,
      # superficie de ataque chica — buen material de charla). Todo el stack ya
      # corrió en arm64 (kind sobre Apple Silicon), así que ARM es riesgo cero.
      # Bleeding edge: cambia a ["m9g.large"] (Graviton5, GA jun 2026) si el MNG
      # lo acepta en tu cuenta; m8g es la opción probada. Evita *.medium: en EKS
      # con VPC CNI los medium Graviton topan ~8 pods/nodo y el stack trae ~45.
      instance_types = ["m8g.large"]
      ami_type       = "BOTTLEROCKET_ARM_64"
      min_size       = 2
      max_size       = 3
      desired_size   = 2 # honrado solo al crear; el módulo lo ignora en applies posteriores
    }
  }

  tags = { Environment = "demo" }
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "configure_kubectl" {
  description = "Tras 'tofu apply', conecta kubectl:"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}"
}
