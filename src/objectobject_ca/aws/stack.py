import logging

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from constructs import Construct

BASE_STACK_NAME = "objectobject-ca"


class ObjectObjectStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        *,
        deployment_stage: str,
        env: cdk.Environment,
    ):
        stack_name = f"{deployment_stage}-{BASE_STACK_NAME}"

        logging.getLogger(__name__).info(f"Initializing stack: {stack_name}")
        super().__init__(
            scope,
            deployment_stage,
            stack_name=stack_name,
            env=env,
        )

        # service

        iam.Role(
            self,
            "CodeDeployServiceRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSCodeDeployRole"
                ),
            ],
        )

        # instance

        instance_user = iam.User(
            self,
            "CodeDeployInstanceUser",
        )

        instance_role = iam.Role(
            self,
            "CodeDeployInstanceRole",
            assumed_by=instance_user,
        )
        instance_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:Get*",
                    "s3:List*",
                ],
                resources=["*"],
            )
        )
        instance_role.grant_assume_role(instance_user)
