import logging

import aws_cdk as cdk
from constructs import Construct

from objectobject_ca.aws.stack import ObjectObjectStack
from objectobject_ca.common.logging import setup_logging


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Creating app.")
    app = cdk.App()

    logger.info("Creating stacks.")
    init_stacks(app)

    logger.info("Synthesizing app.")
    app.synth()

    print()


def init_stacks(app: Construct):
    ObjectObjectStack(
        app,
        deployment_stage="prod",
        env=cdk.Environment(
            account="511603859520",
            region="us-east-1",
        ),
    )


if __name__ == "__main__":
    main()
