terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.53" # EKS v21 exige aws >= 6.52
    }
  }
}

provider "aws" {
  region = var.region
}
