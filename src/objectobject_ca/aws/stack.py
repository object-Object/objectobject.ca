import logging

import aws_cdk as cdk
from aws_cdk import aws_iam as iam, aws_s3 as s3
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

        # artifacts

        artifacts_bucket = s3.Bucket(
            self,
            "CodeDeployArtifacts",
            bucket_name=f"{self.stack_name}-codedeploy-artifacts",
            removal_policy=cdk.RemovalPolicy.DESTROY,
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
        artifacts_bucket.grant_read(instance_role)

        instance_role.grant_assume_role(instance_user)

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
