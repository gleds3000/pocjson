# Provedor AWS
provider "aws" {
  region = var.aws_region
}

# --- CloudWatch Log Group para logs do ECS ---
resource "aws_cloudwatch_log_group" "ecs_task_logs" {
  name              = "/ecs/${var.project_name}-task"
  retention_in_days = 7 # Define por quantos dias os logs serão mantidos
}

# --- ECS Task Definition ---
# Descreve como sua aplicação será executada (imagem Docker, portas, recursos)
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256" # 0.25 vCPU
  memory                   = "512" # 0.5 GB
  execution_role_arn       = var.existing_ecs_task_execution_role_arn # Referencia o IAM Role existente

  # --- INÍCIO DA ALTERAÇÃO PARA GRAVITON2 ---
  # Adicionamos a compatibilidade de CPU para ARM64
  runtime_platform {
    cpu_architecture = "ARM64"
    operating_system_family = "LINUX" # Linux é o SO padrão para Fargate Graviton2
  }
  # --- FIM DA ALTERAÇÃO PARA GRAVITON2 ---

  container_definitions = jsonencode([
    {
      name        = var.project_name
      image       = "${var.existing_ecr_repository_url}:latest" # Referencia a URL do seu repositório ECR existente
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = var.app_port
          hostPort      = var.app_port
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_task_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-task"
  }
}

# --- ALB Target Group ---
# Onde o ALB enviará o tráfego para suas tarefas ECS
resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-tg"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.existing_vpc_id # Referencia o ID da sua VPC existente
  target_type = "ip" # Fargate usa targets IP

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.project_name}-tg"
  }
}

# --- ALB Listener Rule ---
# Define como o tráfego do Listener do ALB será roteado para o Target Group
resource "aws_lb_listener_rule" "app" {
  listener_arn = var.existing_alb_listener_arn # Referencia o ARN do seu Listener ALB existente
  priority     = 100 # Defina uma prioridade que não entre em conflito com regras existentes

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }

  condition {
    path_pattern {
      values = ["/*"] # Roteia todo o tráfego para este serviço. Ajuste conforme necessário.
    }
  }

  tags = {
    Name = "${var.project_name}-listener-rule"
  }
}

# --- ECS Service ---
# Garante que um número desejado de instâncias da sua aplicação esteja sempre em execução
resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = var.existing_ecs_cluster_arn # Referencia o ARN do seu Cluster ECS existente
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1 # Mantém 1 instância da sua aplicação rodando
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.existing_public_subnet_ids # Referencia os IDs das suas subnets públicas existentes
    security_groups  = [var.existing_ecs_tasks_security_group_id] # Referencia o Security Group existente para as tarefas
    assign_public_ip = true # Necessário para que o Fargate possa acessar o ECR e Internet
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.project_name
    container_port   = var.app_port
  }

  # Para evitar problemas de "service is stable" durante a implantação
  depends_on = [aws_lb_listener_rule.app]

  tags = {
    Name = "${var.project_name}-service"
  }
}
