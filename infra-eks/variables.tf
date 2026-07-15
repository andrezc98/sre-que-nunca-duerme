variable "region" {
  description = "Región AWS (los perfiles de inferencia us.* de Bedrock enrutan us-east-1/2 y us-west-2)."
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  type    = string
  default = "eks-demo"
}

variable "kubernetes_version" {
  type    = string
  default = "1.33"
}

# VPC EXISTENTE donde se despliega (no se crea red nueva, se reutiliza su IGW).
# Valor real en terraform.tfvars (gitignored): este repo es público y los IDs
# de infraestructura ajena no se comitean. Ver example.tfvars.
variable "vpc_id" {
  type = string
}

# Subnets NUEVAS a crear desde un CIDR secundario de la VPC, en >=2 AZs
# estándar (requisito del control plane de EKS; las Local Zones no cuentan).
# Públicas: la VPC destino no tiene NAT y crear uno para una demo es gasto
# innecesario — los nodos salen directo por el IGW existente.
variable "public_subnets" {
  type = map(object({
    cidr = string
    az   = string
  }))
}
