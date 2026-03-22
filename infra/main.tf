# Root module for ai-knowledge-assistant infrastructure.
# Add providers, resources, and modules as the project grows.

locals {
  project_name = "ai-knowledge-assistant"
}

output "project_name" {
  description = "Project identifier used for tagging and naming."
  value       = local.project_name
}
