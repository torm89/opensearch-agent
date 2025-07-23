# module "opensearch_knowledge" {
#   source = "terraform-aws-modules/opensearch/aws//modules/collection"
#
#   name             = "opensearch-agent-${var.env}-knowledge"
#   type             = "VECTORSEARCH"
#   standby_replicas = "DISABLED"
#
#   create_access_policy  = true
#   create_network_policy = true
#
#   access_policy_principals = [
#     data.aws_caller_identity.current.arn,
#     # module.lambda_langgraph.lambda_role_arn
#   ]
# }
#
# resource "opensearch_index" "knowledge_opensearch_docs" {
#   name                = "opensearch-agent-${var.env}-knowledge-opensearch-docs"
#   number_of_shards    = 2
#   number_of_replicas  = 0
#   index_knn           = true
#   index_knn_algo_param_ef_search = 512
#
#   mappings = jsonencode({
#     properties = {
#       "vector_field" = {
#         type        = "knn_vector"
#         dimension   = 1024
#         method = {
#           name      = "hnsw"
#           engine    = "faiss"
#           parameters = {
#             m               = 16
#             ef_construction = 512
#           }
#           space_type = "l2"
#         }
#       }
#       "text" = {
#         type = "text"
#       }
#       "metadata" = {
#         type = "object"
#         enabled = true
#       }
#     }
#   })
#
#   depends_on = [module.opensearch_knowledge]
#
#   lifecycle {
#     ignore_changes = all
#   }
# }
#
