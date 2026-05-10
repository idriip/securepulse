package main

# Deny containers running as root
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.securityContext.runAsNonRoot
  msg := sprintf("Container '%s' must set runAsNonRoot: true", [container.name])
}

# Deny containers without resource limits
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.limits
  msg := sprintf("Container '%s' must have resource limits defined", [container.name])
}

# Deny containers with privileged access
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  container.securityContext.privileged == true
  msg := sprintf("Container '%s' must not run as privileged", [container.name])
}

# Deny containers that allow privilege escalation
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  container.securityContext.allowPrivilegeEscalation == true
  msg := sprintf("Container '%s' must not allow privilege escalation", [container.name])
}

# Deny containers without read-only root filesystem
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.securityContext.readOnlyRootFilesystem
  msg := sprintf("Container '%s' must have a read-only root filesystem", [container.name])
}

# Deny deployments without security context
deny contains msg if {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext
  msg := "Deployment must have a pod-level securityContext defined"
}

# Deny latest image tag
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf("Container '%s' must not use the ':latest' image tag", [container.name])
}