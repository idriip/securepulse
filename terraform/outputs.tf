output "ecr_repository_url" {
  description = "ECR repository URL to push Docker images to"
  value       = aws_ecr_repository.securepulse.repository_url
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "eks_cluster_version" {
  description = "Kubernetes version running on the cluster"
  value       = aws_eks_cluster.main.version
}

output "aws_region" {
  description = "AWS region resources are deployed in"
  value       = var.aws_region
}