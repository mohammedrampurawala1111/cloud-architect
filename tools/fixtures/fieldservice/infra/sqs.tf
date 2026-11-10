resource "aws_sqs_queue" "jobs_dlq" { name = "jobs-dlq" }

resource "aws_sqs_queue" "jobs" {
  name           = "jobs"
  redrive_policy = jsonencode({ deadLetterTargetArn = aws_sqs_queue.jobs_dlq.arn, maxReceiveCount = 5 })
}
