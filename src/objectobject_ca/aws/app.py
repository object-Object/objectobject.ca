import logging
from typing import TypedDict

import aws_cdk as cdk

from ..common.logging import setup_logging
from .stack import AWSStack

logger = logging.getLogger(__name__)


class CommonKwargs(TypedDict):
    oidc_owner: str
    oidc_repo: str


def main():
    setup_logging()

    logger.info("Ready.")
    app = cdk.App()

    common = CommonKwargs(
        oidc_owner="object-Object",
        oidc_repo="objectobject.ca",
    )

    AWSStack(
        app,
        "prod",
        env=cdk.Environment(
            account="511603859520",
            region="us-east-1",
        ),
        oidc_env_cdk="prod-aws-cdk",
        oidc_env_codedeploy="prod-codedeploy",
        on_premise_instance_tag="prod-objectobject-ca",
        **common,
    )

    logger.info("Synthesizing.")
    app.synth()


if __name__ == "__main__":
    main()
