import aws_cdk as cdk
from aws_cdk import (
    aws_cloudformation as cloudformation,
    aws_iam as iam,
)
from constructs import Construct

cloudformation.CfnTypeActivation


class ResourceTypeActivation(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        type_name: str,
        publisher_id: str,
        source_arn_resource_name: str,
    ):
        super().__init__(scope, id)

        self.role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.ServicePrincipal(
                "resources.cloudformation.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": self._stack.account,
                    },
                    "StringLike": {
                        "aws:SourceArn": cdk.Arn.format(
                            cdk.ArnComponents(
                                service="cloudformation",
                                resource="type/resource",
                                resource_name=source_arn_resource_name,
                            ),
                            self._stack,
                        ),
                    },
                },
            ),
        )

        self.type_activation = cloudformation.CfnTypeActivation(
            self,
            "TypeActivation",
            type="RESOURCE",
            type_name=type_name,
            publisher_id=publisher_id,
            execution_role_arn=self.role.role_arn,
        )

    @property
    def _stack(self):
        return cdk.Stack.of(self)
