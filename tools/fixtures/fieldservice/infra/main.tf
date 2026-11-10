# One ECS cluster on Fargate runs two services from the same image: api and worker.
resource "aws_ecs_cluster" "main" { name = "fieldservice" }

resource "aws_ecs_service" "api" {
  name          = "api"
  cluster       = aws_ecs_cluster.main.id
  desired_count = 2
  launch_type   = "FARGATE"
}

resource "aws_ecs_service" "worker" {
  name          = "worker"
  cluster       = aws_ecs_cluster.main.id
  desired_count = 1
  launch_type   = "FARGATE"
}

resource "aws_db_instance" "main" {
  engine              = "postgres"
  engine_version      = "16"
  instance_class      = "db.t4g.medium"
  multi_az            = true
  deletion_protection = true
}

resource "aws_cognito_user_pool" "users" { name = "fieldservice-users" }
