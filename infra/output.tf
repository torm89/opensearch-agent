output "agent_runtime_name" {
  value = local.agent_name
}

output "agent_runtime_role_arn" {
  value = aws_iam_role.agent_runtime.arn
}

output "knowledge_opensearch_collection_url" {
  value = module.opensearch_collection.endpoint
}

output "knowledge_opensearch_opensearch_index_name" {
  value = module.opensearch_collection.name
}
