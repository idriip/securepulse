# ── Security Groups (base — no rules) ─────────────────────────────────────────
resource "aws_security_group" "eks_cluster" {
  name        = "${var.project_name}-eks-cluster-sg"
  description = "Security group for EKS cluster control plane"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_security_group" "eks_nodes" {
  name        = "${var.project_name}-eks-nodes-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for the application load balancer"
  vpc_id      = module.vpc.vpc_id
}

# ── Cluster Rules ──────────────────────────────────────────────────────────────
resource "aws_security_group_rule" "cluster_ingress_nodes" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  description              = "Allow worker nodes to communicate with control plane"
  security_group_id        = aws_security_group.eks_cluster.id
  source_security_group_id = aws_security_group.eks_nodes.id
}

resource "aws_security_group_rule" "cluster_egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  description       = "Allow all outbound traffic"
  security_group_id = aws_security_group.eks_cluster.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# ── Node Rules ─────────────────────────────────────────────────────────────────
resource "aws_security_group_rule" "nodes_ingress_self" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  description       = "Allow nodes to communicate with each other"
  security_group_id = aws_security_group.eks_nodes.id
  self              = true
}

resource "aws_security_group_rule" "nodes_ingress_cluster" {
  type                     = "ingress"
  from_port                = 1025
  to_port                  = 65535
  protocol                 = "tcp"
  description              = "Allow control plane to communicate with worker nodes"
  security_group_id        = aws_security_group.eks_nodes.id
  source_security_group_id = aws_security_group.eks_cluster.id
}

resource "aws_security_group_rule" "nodes_ingress_alb" {
  type                     = "ingress"
  from_port                = 8000
  to_port                  = 8000
  protocol                 = "tcp"
  description              = "Allow load balancer to reach app port"
  security_group_id        = aws_security_group.eks_nodes.id
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "nodes_egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  description       = "Allow all outbound traffic"
  security_group_id = aws_security_group.eks_nodes.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# ── ALB Rules ──────────────────────────────────────────────────────────────────
resource "aws_security_group_rule" "alb_ingress_http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  description       = "Allow HTTP from internet"
  security_group_id = aws_security_group.alb.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "alb_ingress_https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  description       = "Allow HTTPS from internet"
  security_group_id = aws_security_group.alb.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "alb_egress_nodes" {
  type                     = "egress"
  from_port                = 8000
  to_port                  = 8000
  protocol                 = "tcp"
  description              = "Allow outbound to worker nodes only"
  security_group_id        = aws_security_group.alb.id
  source_security_group_id = aws_security_group.eks_nodes.id
}