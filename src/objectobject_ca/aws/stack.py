import logging
from typing import Iterable

import aws_cdk as cdk
from aws_cdk import aws_iam as iam, aws_s3 as s3, aws_ssm as ssm
from aws_cdk_github_oidc import GithubActionsIdentityProvider, GithubActionsRole
from constructs import Construct

BASE_STACK_NAME = "objectobject-ca"


class ObjectObjectStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        *,
        deployment_stage: str,
        env: cdk.Environment,
        oidc_owner: str,
        oidc_environment: str,
        instance_secure_string_parameter_names: Iterable[str],
    ):
        stack_name = f"{deployment_stage}-{BASE_STACK_NAME}"

        logging.getLogger(__name__).info(f"Initializing stack: {stack_name}")
        super().__init__(
            scope,
            deployment_stage,
            stack_name=stack_name,
            env=env,
        )

        # external resources

        cdk_role_proxy = iam.Role.from_role_arn(
            self,
            "CDKRoleProxy",
            f"arn:aws:iam::{self.account}:role/cdk-*",
        )

        parameter_proxies = [
            ssm.StringParameter.from_secure_string_parameter_attributes(
                self,
                f"{parameter_name}Proxy",
                parameter_name=parameter_name,
            )
            for parameter_name in instance_secure_string_parameter_names
        ]

        # OpenID Connect

        github_oidc_provider = GithubActionsIdentityProvider(
            self,
            "GitHubOIDCProvider",
        )

        # GitHub Actions

        github_actions_cdk_role = GithubActionsRole(
            self,
            "GitHubActionsCDKRole",
            provider=github_oidc_provider,
            owner=oidc_owner,
            repo="*",
            filter=f"environment:{oidc_environment}",
        )
        cdk_role_proxy.grant_assume_role(github_actions_cdk_role)

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
        instance_role.grant_assume_role(instance_user)
        for parameter in parameter_proxies:
            parameter.grant_read(instance_role)

        # artifacts

        artifacts_bucket = s3.Bucket(
            self,
            "CodeDeployArtifacts",
            bucket_name=f"{self.stack_name}-codedeploy-artifacts",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        artifacts_bucket.grant_read(instance_role)

        # outputs

        cdk.CfnOutput(
            self,
            "GitHubActionsCDKRoleARN",
            value=github_actions_cdk_role.role_arn,
        )

        cdk.CfnOutput(
            self,
            "CodeDeployArtifactsBucketName",
            value=artifacts_bucket.bucket_name,
        )
