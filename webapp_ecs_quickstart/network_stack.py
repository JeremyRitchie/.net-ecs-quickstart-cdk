from aws_cdk import (
    aws_ec2 as ec2,
    aws_route53 as r53,
    Stack
)

from constructs import Construct
from env_config import environments

class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, env_name, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.stack = 'networking'
        self.env = environments[env_name]

        self.vpc = ec2.Vpc(
            self,
            "VPC",
            ip_addresses=ec2.IpAddresses.cidr(self.env.networking.vpc_cidr_range),
            max_azs=3,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Presentation Subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Application Subnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Data Subnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                ),
            ],
            nat_gateways=1
        )

