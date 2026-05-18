output "ecr_repository_url" {
  description = "ECR repository URL to push Docker images to"
  value       = aws_ecr_repository.securepulse.repository_url
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_version" {
  description = "Kubernetes version running on the cluster"
  value       = module.eks.cluster_version
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "Private subnet IDs where worker nodes run"
  value       = module.vpc.private_subnets
}

output "aws_region" {
  description = "AWS region resources are deployed in"
  value       = var.aws_region
}
