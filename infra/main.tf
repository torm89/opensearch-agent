provider "aws" {
  region = var.region
}

# provider "awscc" {
#   region = "us-east-1"
# }

# provider "opensearch" {
#   url         = module.opensearch_knowledge.endpoint
#   healthcheck = false
# }

locals {
  agent_name = "opensearch-agent-${var.env}"
}
