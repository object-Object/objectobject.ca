#!/bin/bash
set -euox pipefail

cd /var/lib/codedeploy-apps/objectobject-ca

# grafana alloy

if sudo systemctl is-active --quiet alloy ; then
    sudo systemctl reload alloy
else
    sudo systemctl start alloy
fi

# application

docker login ghcr.io --username object-Object --password-stdin < /var/lib/codedeploy-apps/.cr_pat

if ! docker compose up --detach --wait --wait-timeout 120 ; then
    docker compose logs
    exit 1
fi
