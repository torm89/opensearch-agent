output "agent_runtime_name" {
  value = local.agent_name
}

output "agent_runtime_role_arn" {
  value = aws_iam_role.agent_runtime.arn
}
