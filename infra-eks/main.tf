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
    eks-pod-identity-agent = { before_compute = true } # requerido para Pod Identity (Bedrock)
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.large"]
      ami_type       = "AL2023_x86_64_STANDARD"
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
