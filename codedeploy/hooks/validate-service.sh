#!/bin/bash
set -euox pipefail

cd /var/lib/codedeploy-apps/objectobject-ca

# grafana alloy

sleep 15
if ! sudo systemctl is-active --quiet alloy ; then
    sudo journalctl -u alloy -n 100 --no-pager
    exit 1
fi
