provider "aws" {
  region = var.region
}

# provider "awscc" {
#   region = "us-east-1"
# }

provider "opensearch" {
  url         = module.opensearch_collection.endpoint
  healthcheck = false
}

locals {
  agent_name = "OpensearchAgent${title(var.env)}"
}
