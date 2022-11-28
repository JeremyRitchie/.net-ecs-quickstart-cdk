from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elb,
    aws_route53 as r53,
    aws_route53_targets as r53_targets,
    aws_certificatemanager as acm,
    aws_logs as logs,
    Stack
)

from constructs import Construct
from env_config import environments
from webapp_ecs_quickstart.network_stack import NetworkStack

class ComputeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, network: NetworkStack, env_name, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = network.vpc
        self.env = environments[env_name]
        self.stack = 'container'

        self.log_group = logs.LogGroup(
            self,
            "LogGroup",
            retention=logs.RetentionDays.THREE_MONTHS,
            log_group_name=f"/aws/ecs/{self.env.compute.app_name}-{env_name}",
        )

        self.cluster_sg = ec2.SecurityGroup(
            self,
            "Cluster_SG",
            security_group_name=f"cluster-sg-{self.env.compute.app_name}-{env_name}",
            vpc=self.vpc,
            description="Security Group for ECS Tasks",
            allow_all_outbound=True
        )

        self.alb_sg = ec2.SecurityGroup(
            self,
            "LoadBalancer_SG",
            security_group_name=f"alb-sg-{self.env.compute.app_name}-{env_name}",
            vpc=self.vpc,
            description="Security Group for ALB",
            allow_all_outbound=True
        )

        # Add cluster ingress rules
        self.cluster_sg.add_ingress_rule(peer=self.alb_sg,
                                  connection=ec2.Port.tcp(8080),
                                  description="Open Port from ALB to Tasks")


        self.alb_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(),
                            connection=ec2.Port.tcp(80),
                            description="Open Port from ALB to World")

        self.alb_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(),
                    connection=ec2.Port.tcp(443),
                    description="Open Port from ALB to World")

        self.alb = elb.ApplicationLoadBalancer(
            self,
            "ALB",
            security_group=self.alb_sg,
            vpc=self.vpc,
            internet_facing= True,
            load_balancer_name=f"alb-{self.env.compute.app_name}-{env_name}",
        )

        self.alb_target_group = elb.ApplicationTargetGroup(
            self,
            "TargetGroup",
            port = 80,
            protocol = elb.ApplicationProtocol.HTTP,
            vpc = self.vpc,
            target_group_name = f"target-group-{self.env.compute.app_name}-{env_name}",
            health_check=elb.HealthCheck(
                enabled=True,
                path="/ready"
            ),
        )

        self.listener = elb.ApplicationListener(
            self,
            "Http-Listener",
            load_balancer = self.alb,
            protocol=elb.ApplicationProtocol.HTTP,
            port = 80,
            default_target_groups = [self.alb_target_group],
        )

        self.task_role = iam.Role(
            self,
            'Task_Role',
            assumed_by=iam.ServicePrincipal(service='ecs-tasks.amazonaws.com'),
            role_name=f"task-role-{self.env.compute.app_name}-{env_name}",
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name='service-role/AmazonECSTaskExecutionRolePolicy'
            )],
            inline_policies={
                "Task": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["ecs:StartTelemetrySession", "cloudwatch:*"],
                            effect=iam.Effect.ALLOW,
                            resources = ["*"]
                        )
                    ]
                )
            }
        )

        self.task_definition = ecs.FargateTaskDefinition(self,
            "TaskDefinition",
            cpu = 512,
            memory_limit_mib = 1024,
            execution_role = self.task_role,
            task_role = self.task_role,
            family = f"{self.env.compute.app_name}-{env_name}",
            )

        self.task_definition.add_container(
            "Nginx Hello World",
            image=ecs.ContainerImage.from_registry(self.env.compute.image),
            port_mappings = [ecs.PortMapping(container_port=80, host_port=80)],
            container_name = f"{self.env.compute.app_name}-{env_name}",
            logging=ecs.AwsLogDriver(
                stream_prefix=env_name,
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                log_group=self.log_group)
        )

        self.cluster = ecs.Cluster(
            self,
            "Cluster",
            cluster_name = f"cluster-{self.env.compute.app_name}-{env_name}",
            container_insights = True,
            enable_fargate_capacity_providers = True,
            vpc = self.vpc
        )

        self.service = ecs.FargateService(
            self,
            "Service",
            task_definition = self.task_definition,
            security_groups = [self.cluster_sg],
            cluster = self.cluster,
            desired_count = 2,
            enable_ecs_managed_tags = True,
            service_name = f"service-{self.env.compute.app_name}-{env_name}",
        )

        self.alb_target_group.add_target(
            self.service
        )