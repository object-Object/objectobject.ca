import logging
from typing import TypedDict

import aws_cdk as cdk

from ..common.logging import setup_logging
from .stack import AWSStack

logger = logging.getLogger(__name__)


class CommonKwargs(TypedDict):
    oidc_owner: str


def main():
    setup_logging()

    logger.info("Ready.")
    app = cdk.App()

    common = CommonKwargs(
        oidc_owner="object-Object",
    )

    AWSStack(
        app,
        deployment_stage="prod",
        env=cdk.Environment(
            account="511603859520",
            region="us-east-1",
        ),
        oidc_environment="prod-aws-cdk",
        instance_secure_string_parameter_names=[
            "/prod/HexBug/*",
        ],
        **common,
    )

    logger.info("Synthesizing.")
    app.synth()


if __name__ == "__main__":
    main()
