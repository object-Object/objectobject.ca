import logging

import aws_cdk as cdk
from aws_cdk import (
    aws_codedeploy as codedeploy,
    aws_iam as iam,
    aws_s3 as s3,
)
from aws_cdk_github_oidc import GithubActionsIdentityProvider, GithubActionsRole
from constructs import Construct

from .utils.cfn import ResourceTypeActivation

BASE_STACK_NAME = "objectobject-ca"

logger = logging.getLogger(__name__)


class AWSStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        deployment_stage: str,
        *,
        env: cdk.Environment,
        oidc_owner: str,
        oidc_repo: str,
        on_premise_instance_tag: str,
        oidc_environment: str,
    ):
        stack_name = f"{deployment_stage}-{BASE_STACK_NAME}"

        logger.info(f"Initializing stack: {stack_name}")
        super().__init__(
            scope,
            deployment_stage,
            stack_name=stack_name,
            env=env,
        )

        # external resource proxies

        cdk_role_proxy = iam.Role.from_role_arn(
            self,
            "CDKRoleProxy",
            f"arn:aws:iam::{self.account}:role/cdk-*",
        )

        # OIDC provider for GitHub Actions workflows
        github_oidc_provider = GithubActionsIdentityProvider(
            self,
            "GitHubOIDCProvider",
        )

        # role assumed by all GitHub Actions workflows to deploy CDK stacks
        github_actions_cdk_role = GithubActionsRole(
            self,
            "GitHubActionsCDKRole",
            provider=github_oidc_provider,
            owner=oidc_owner,
            repo="*",  # *all* of my repos assume this role, not just this one
            filter=f"environment:{oidc_environment}",
        )
        cdk_role_proxy.grant_assume_role(github_actions_cdk_role)

        # user and role for the Vultr VPS to use for CodeDeploy
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

        # common CodeDeploy artifact bucket
        artifacts_bucket = s3.Bucket(
            self,
            "CodeDeployArtifacts",
            bucket_name=f"{self.stack_name}-codedeploy-artifacts",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        artifacts_bucket.grant_read(instance_role)

        # custom resource types
        ResourceTypeActivation(
            self,
            "CloudflareDnsRecordTypeActivation",
            type_name="Cloudflare::Dns::Record",
            publisher_id="c830e97710da0c9954d80ba8df021e5439e7134b",
            source_arn_resource_name="Cloudflare-Dns-Record/*",
        )

        # CodeDeploy stuff for this repo

        application = codedeploy.ServerApplication(
            self,
            "Application",
        )

        deployment_config: codedeploy.ServerDeploymentConfig = (
            codedeploy.ServerDeploymentConfig.ONE_AT_A_TIME
        )

        group = codedeploy.ServerDeploymentGroup(
            self,
            "DeploymentGroup",
            application=application,
            deployment_config=deployment_config,
            auto_rollback=codedeploy.AutoRollbackConfig(
                failed_deployment=True,
            ),
            on_premise_instance_tags=codedeploy.InstanceTagSet(
                {"instance": [on_premise_instance_tag]}
            ),
        )

        actions_role = GithubActionsRole(
            self,
            "ActionsCodeDeployRole",
            provider=github_oidc_provider,
            owner=oidc_owner,
            repo=oidc_repo,
            filter=f"environment:{oidc_environment}",
        )
        artifacts_bucket.grant_read_write(actions_role)
        actions_role.add_to_policy(
            iam.PolicyStatement(
                actions=["codedeploy:*"],
                resources=[
                    application.application_arn,
                    group.deployment_group_arn,
                    deployment_config.deployment_config_arn,
                ],
            )
        )

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

        cdk.CfnOutput(self, "ApplicationName", value=application.application_name)
        cdk.CfnOutput(self, "DeploymentGroupName", value=group.deployment_group_name)
        cdk.CfnOutput(self, "ActionsCodeDeployRoleARN", value=actions_role.role_arn)
