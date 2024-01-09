import logging
import os
from typing import Any

import cdktf
from cdktf_cdktf_provider_cloudflare import provider, record
from constructs import Construct

VULTR_VPS = "155.138.139.1"


class TerraformStack(cdktf.TerraformStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        organization: str,
        workspace: str,
        zone_id: str,
    ):
        logging.getLogger(__name__).info(f"Initializing stack: {id}")
        super().__init__(scope, id)

        cdktf.CloudBackend(
            self,
            organization=organization,
            workspaces=cdktf.NamedCloudWorkspace(workspace),
        )

        provider.CloudflareProvider(
            self,
            "CloudflareProvider",
            api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
        )

        # simple records
        for record_type, records in {
            "A": {
                # main server
                "@": VULTR_VPS,
                "www": VULTR_VPS,
                "derp": VULTR_VPS,
                "fragments": VULTR_VPS,
                "znc": VULTR_VPS,
                # main server, but not in the SSL cert (idk what these are for)
                "hex": VULTR_VPS,
                "nebula": VULTR_VPS,
                # external stuff
                "dev.hexxycraft": "131.186.1.24",
                "hexxycraft": "23.139.82.245",
                "jupyter": "3.19.84.159",
            },
            "CNAME": {
                # email forwarding
                "_dmarc": "dmarcforward.emailowl.com",
                "dkim._domainkey": "dkim._domainkey.srs.emailowl.com",
            },
        }.items():
            for name, value in records.items():
                create_record(
                    self,
                    zone_id=zone_id,
                    type=record_type,
                    name=name,
                    value=value,
                )

        # MX records (email forwarding)
        for value in [
            "mx4.emailowl.com",
            "mx5.emailowl.com",
            "mx6.emailowl.com",
        ]:
            create_record(
                self,
                zone_id=zone_id,
                type="MX",
                name=None,
                value=value,
                priority=10,
            )

        # TXT records
        for value in [
            # SPF record (email forwarding)
            "v=spf1 a mx ~all",
        ]:
            create_record(
                self,
                zone_id=zone_id,
                type="TXT",
                name=None,
                value=value,
            )


def create_record(
    scope: Construct,
    *,
    zone_id: str,
    type: str,
    name: str | None,
    value: str,
    priority: int | None = None,
    proxied: bool = False,
    **kwargs: Any,
):
    match name:
        case "@":
            id_parts = [type, "ROOT", value]
        case str():
            id_parts = [type, name, value]
        case None:
            id_parts = [type, value]
            name = "@"

    return record.Record(
        scope,
        "_".join(id_parts).replace(".", "-"),
        zone_id=zone_id,
        type=type,
        name=name,
        value=value,
        priority=priority,
        proxied=proxied,
        **kwargs,
    )
