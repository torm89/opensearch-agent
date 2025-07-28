module "opensearch_collection" {
  source = "terraform-aws-modules/opensearch/aws//modules/collection"

  name             = "opensearch-agent-${var.env}"
  type             = "VECTORSEARCH"
  standby_replicas = "DISABLED"

  create_access_policy  = true
  create_network_policy = true

  access_policy_name = "oa-${var.env}-knowledge-access"
  network_policy_name = "oa-${var.env}-knowledge-network"
  encryption_policy_name = "oa-${var.env}-knowledge-encryption"

  access_policy_principals = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
    data.aws_caller_identity.current.arn,
    aws_iam_role.agent_runtime.arn
  ]
}

resource "opensearch_index" "knowledge_opensearch_docs" {
  name                = "opensearch-agent-${var.env}-knowledge-opensearch-docs"
  number_of_shards    = 2
  number_of_replicas  = 0
  index_knn           = true
  index_knn_algo_param_ef_search = 512

  mappings = jsonencode({
    properties = {
      "vector_field" = {
        type        = "knn_vector"
        dimension   = 1024
        method = {
          name      = "hnsw"
          engine    = "faiss"
          parameters = {
            m               = 16
            ef_construction = 512
          }
          space_type = "l2"
        }
      }
      "text" = {
        type = "text"
      }
      "metadata" = {
        type = "object"
        enabled = true
      }
    }
  })

  depends_on = [module.opensearch_collection]

  lifecycle {
    ignore_changes = all
  }
}

