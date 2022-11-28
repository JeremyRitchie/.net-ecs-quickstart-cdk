import aws_cdk as cdk
from constructs import Construct

from webapp_ecs_quickstart.network_stack import NetworkStack
from webapp_ecs_quickstart.compute_stack import ComputeStack


class PipelineStage(cdk.Stage):
    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.network = NetworkStack(
            self,
            "network",
            env=cdk.Environment(
                account=self.node.try_get_context(f"account:{env_name}"),
                region=self.node.try_get_context(f"region:{env_name}"),
            ),
            env_name=env_name
        )
        self.compute = ComputeStack(
            self,
            "compute",
            network=self.network,
            env=cdk.Environment(
                account=self.node.try_get_context(f"account:{env_name}"),
                region=self.node.try_get_context(f"region:{env_name}"),
            ),
            env_name=env_name
        )