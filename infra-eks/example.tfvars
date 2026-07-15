# Copia a terraform.tfvars (gitignored) y pon los valores reales de tu VPC.
vpc_id = "vpc-XXXXXXXXXXXXXXXXX"

# CIDRs libres dentro de un bloque secundario de la VPC, en dos AZs estándar.
public_subnets = {
  a = { cidr = "10.222.10.0/24", az = "us-east-1a" }
  b = { cidr = "10.222.11.0/24", az = "us-east-1b" }
}
