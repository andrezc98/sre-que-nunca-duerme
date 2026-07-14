variable "region" {
  description = "Región AWS. Bedrock Claude Sonnet 4.6 se sirve vía perfil de inferencia US."
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  type    = string
  default = "kcd-demo"
}

variable "kubernetes_version" {
  type    = string
  default = "1.33"
}
