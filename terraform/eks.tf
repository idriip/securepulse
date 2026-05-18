module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project_name}-eks"
  cluster_version = var.eks_cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  cluster_security_group_id = aws_security_group.eks_cluster.id

  eks_managed_node_groups = {
    main = {
      instance_types = [var.eks_node_instance_type]
      min_size       = var.eks_min_nodes
      max_size       = var.eks_max_nodes
      desired_size   = var.eks_desired_nodes

      subnet_ids = module.vpc.private_subnets

      vpc_security_group_ids = [aws_security_group.eks_nodes.id]

      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 20
            volume_type           = "gp3"
            encrypted             = true
            delete_on_termination = true
          }
        }
      }
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }
}