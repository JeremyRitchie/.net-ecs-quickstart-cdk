from aws_cdk import aws_ec2 as ec2


from typing import Dict, Optional
from dataclasses import dataclass, field
from aws_cdk import aws_ec2 as ec2

@dataclass
class Networking:
    vpc_cidr_range: str


@dataclass
class Compute:
    app_name: str
    image: str

@dataclass
class Environment:
    networking: Networking
    compute: Compute
    version_control_branch: str


@dataclass
class Tooling:
    github_repo: str
    codestar_connection_arn: str

tooling = Tooling(
    "jeremyritchie/dotnet-ecs-quickstart-cdk",
    "arn:aws:codestar-connections:ap-southeast-2:915922766016:connection/2086386e-a6b9-42de-873b-fb1de796170d",
)

environments: Dict[str, Environment] = {
    "DEV": Environment(
        Networking(
            vpc_cidr_range="10.0.0.0/16",
        ),
        Compute(
            app_name="dotnet-demo",
            image="mcr.microsoft.com/dotnet/samples:dotnetapp"
        ),
        version_control_branch="main",
    ),
    "UAT": Environment(
        Networking(
            vpc_cidr_range="10.1.0.0/16",
        ),
        Compute(
            app_name="dotnet-demo",
            image="mcr.microsoft.com/dotnet/samples:dotnetapp"
        ),
        version_control_branch="main",
    ),
    "PROD": Environment(
        Networking(
            vpc_cidr_range="10.2.0.0/16",
        ),
        Compute(
            app_name="dotnet-demo",
            image="mcr.microsoft.com/dotnet/samples:dotnetapp"
        ),
        version_control_branch="main",
    ),
}