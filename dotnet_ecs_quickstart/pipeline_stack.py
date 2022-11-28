"""Module to create a CDK Codepipeline stacks

This creates a pipeline per-environment to deploy application stacks,
plus a self-mutation pipeline for this repository
"""

from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
)
import aws_cdk as cdk

from dotnet_ecs_quickstart.pipeline_stage import PipelineStage
from env_config import tooling, environments


class PipelineStack(Stack):
    """Create pipelines to deploy this stack and environment stacks"""

    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        project = self.node.try_get_context("project_name")

        application_pipeline = pipelines.CodePipeline(
            self,
            f"{project}-pipeline",
            pipeline_name=f"{project}-{env_name}-pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    repo_string=tooling.github_repo,
                    branch=environments[env_name].version_control_branch,
                    connection_arn=tooling.codestar_connection_arn,
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt",
                    "cdk synth",
                ],
            ),
            publish_assets_in_parallel=False,
            cross_account_keys=True,
            self_mutation=True,
            docker_enabled_for_synth=True,
        )

        application_pipeline.add_stage(
            PipelineStage(
                self,
                f"{env_name}",
                env=cdk.Environment(
                    account=self.node.try_get_context(f"account:{env_name}"),
                    region=self.node.try_get_context(f"region:{env_name}"),
                ),
                env_name=env_name,
            ),
            pre=[pipelines.ManualApprovalStep("Deploy Infrastructure")],
        )
