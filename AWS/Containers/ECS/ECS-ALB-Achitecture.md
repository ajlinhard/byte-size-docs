# ECS ALB Architecture
ALB integration with ECS is a first-class, built-in feature. ECS registers and deregisters task targets in an ALB target group automatically as tasks start, stop, and get replaced.
<img width="1472" height="1070" alt="image" src="https://github.com/user-attachments/assets/d37ea017-f689-4024-b62d-42ff47613486" />

## The options

**Target type: `ip`** — required for Fargate, and the usual choice for EC2 launch type with `awsvpc` network mode. Each task gets its own ENI and private IP, and the ALB routes straight to it. Cleanest option, and it lets you use the container port directly.

**Target type: `instance`** — only for EC2 launch type with `bridge` or `host` networking. The ALB routes to the container instance on a dynamically mapped ephemeral port. Works fine, but you're bound to the instance's capacity and it complicates security group rules.

**Other routing choices layered on top:**
- Internet-facing vs internal ALB (internal for service-to-service or behind an API gateway).
- Multiple target groups on one service — useful when a container exposes more than one port, or for blue/green deploys.
- Host-based and path-based listener rules to put several ECS services behind one ALB, which saves a lot of money at small scale.
- NLB instead of ALB for TCP/UDP, static IPs, or extreme throughput. GWLB for inline appliances.
- ECS Service Connect or Cloud Map for east-west traffic, where you often don't want a load balancer at all.

# Infrastructure inventory

**Networking**
- VPC with at least two subnets in two AZs for the ALB. Public subnets plus an internet gateway for an internet-facing ALB.
- Private subnets for the tasks, with a NAT gateway or VPC endpoints (ECR api + dkr, S3, CloudWatch Logs) so tasks can pull images without public IPs.
- Two security groups: one on the ALB allowing 80/443 from the internet, one on the tasks allowing the container port *from the ALB's security group* rather than a CIDR.

**Load balancer side**
- The ALB itself, plus a listener (443 with an ACM certificate, and usually a 80→443 redirect listener).
- A target group per service, with health check path, interval, thresholds, and deregistration delay set. Match the protocol version if you're doing gRPC or HTTP/2.
- Listener rules if you're multiplexing services.
- Optional: S3 bucket for access logs, WAF web ACL.

**Compute side**
- ECS cluster.
- Task definition with a `portMappings` entry for the container, a task execution role (ECR pull, log write), a task role for whatever your app calls, and a log configuration.
- ECS service with a `loadBalancers` block naming the target group ARN, the container name, and the container port. Include a health check grace period so slow-starting apps aren't killed during boot.
- For EC2 launch type: an ASG and capacity provider, plus the ECS agent AMI.

**Around the edges**
- Route 53 alias record to the ALB DNS name.
- Application Auto Scaling policy — target tracking on `ALBRequestCountPerTarget` is the natural metric once an ALB is in front.
- If you want blue/green: a second target group and a test listener, driven by CodeDeploy or ECS's built-in blue/green.

The one thing worth calling out: you do not create or manage the target registrations yourself. Define the target group empty, point the service at it, and ECS handles the rest. People often get tripped up trying to register targets manually or via Terraform, which then fights with the service.
