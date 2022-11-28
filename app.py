#!/usr/bin/env python3
import os

import aws_cdk as cdk

from dotnet_ecs_quickstart.pipeline_stack import PipelineStack
from env_config import environments

app = cdk.App()

for env_name, environment in environments.items():
    PipelineStack(
        app,
        f"dotnet-ecs-quickstart-pipeline-{env_name}",
        env=cdk.Environment(
            account=app.node.try_get_context(f"account:{env_name}"),
            region=app.node.try_get_context(f"region:{env_name}")
        ),
        env_name=env_name
    )

app.synth()

