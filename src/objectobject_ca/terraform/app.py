import logging
from typing import TypedDict

import cdktf

from ..common.logging import setup_logging
from .stack import TerraformStack

logger = logging.getLogger(__name__)


class CommonKwargs(TypedDict):
    organization: str
    workspace: str


def main():
    setup_logging()

    logger.info("Ready.")
    app = cdktf.App()

    common = CommonKwargs(
        organization="object-Object",
        workspace="objectobject-ca",
    )

    TerraformStack(
        app,
        "prod",
        zone_id="c34ef372a8d773ca057615c8a85d719c",
        **common,
    )

    logger.info("Synthesizing.")
    app.synth()


if __name__ == "__main__":
    main()
