import logging
import os

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

        for record_type, name, value, proxied in [
            # main vps
            ("A", "objectobject.ca", VULTR_VPS, False),
            ("A", "www", VULTR_VPS, False),
            ("A", "fragments", VULTR_VPS, False),
            ("A", "hex", VULTR_VPS, False),
            ("A", "nebula", VULTR_VPS, False),
            ("A", "znc", VULTR_VPS, False),
            # external
            ("A", "dev.hexxycraft", "131.186.1.24", False),
            ("A", "hexxycraft", "23.139.82.245", False),
            ("A", "jupyter", "3.19.84.159", False),
            # email forwarding
            ("CNAME", "_dmarc", "dmarcforward.emailowl.com", False),
            ("CNAME", "dkim._domainkey", "dkim._domainkey.srs.emailowl.com", False),
            ("MX", "", "mx4.emailowl.com", False),
            ("MX", "", "mx5.emailowl.com", False),
            ("MX", "", "mx6.emailowl.com", False),
            # i have no idea what this is for
            ("TXT", "", "v=spf1 a mx ~all", False),
        ]:
            record.Record(
                self,
                f"{record_type}_{name}_{value}",
                zone_id=zone_id,
                type=record_type,
                name=name,
                value=value,
                proxied=proxied,
            )
