terraform {
  backend "s3" {
    key            = "tofu-state-opensearch-agent.tfstate"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.3.0"
    }
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "2.3.1"  # Adjust to the desired version
    }
    # awscc = {
    #   source  = "hashicorp/awscc"
    #   version = "~> 1.0"  # Sprawdź najnowszą wersję w registry
    # }
  }

  required_version = ">= 1.2.0"
}
