# objectobject.ca

Monorepo for https://objectobject.ca, including many services and resources that are deployed to my VPS or AWS account and don't belong in any other repository.

## Repository structure

- [.github/workflows/deploy.yml](./.github/workflows/deploy.yml): Deployment workflow for objectobject.ca. Runs on every push to main.
- [codedeploy/](./codedeploy): Files in this directory are uploaded to S3 and deployed to the VPS. Some files are generated and added to this directory by the deployment workflow.
  - [alloy/config.alloy](./codedeploy/alloy/config.alloy): Config file for [Grafana Alloy](https://grafana.com/docs/alloy/latest/). This sets up exporting of metrics and logs to Grafana Cloud for many services on my VPS.
  - [gatus/config.yml](./codedeploy/gatus/config.yml): Config file for https://status.objectobject.ca.
  - [hooks/](./codedeploy/hooks): Bash scripts executed by CodeDeploy during the deployment process.
  - [appspec.yml](./codedeploy/appspec.yml): [AppSpec file](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html) for CodeDeploy. Configures where to copy files and what hooks to execute during a deployment.
  - [compose.override.yml](./codedeploy/compose.override.yml): Development-only configs for Docker Compose.
  - [compose.yml](./codedeploy/compose.yml): Base Docker Compose file for objectobject.ca. This is where most Docker configuration happens, other than a few development- or production-only settings.
- [src/objectobject_ca/](./src/objectobject_ca): Root directory for the `objectobject_ca` Python package.
  - [aws/](./src/objectobject_ca/aws): [AWS CDK](https://aws.amazon.com/cdk/) application for objectobject.ca. This deploys several global resources for my AWS account (eg. the S3 bucket where all CodeDeploy deployment bundles are uploaded), as well as the [CodeDeploy application](https://docs.aws.amazon.com/codedeploy/latest/userguide/applications.html) and [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) that are used for deploying the services in this repository.
  - [common/](./src/objectobject_ca/common): Dependency-free utilities for other packages.
  - [terraform/](./src/objectobject_ca/terraform): [CDKTF](https://developer.hashicorp.com/terraform/cdktf) (CDK for Terraform) application for objectobject.ca. This deploys DNS records to Cloudflare for the objectobject.ca domain.
- [compose.override.yml](./compose.override.yml): Development-only configs for Docker Compose.

## Instance setup

Source: https://docs.aws.amazon.com/codedeploy/latest/userguide/register-on-premises-instance-iam-session-arn.html

* Install:
  * AWS CLI
  * CodeDeploy agent
  * aws-codedeploy-session-helper
* Create an access key for `CodeDeployInstanceUser`. Add it to `/home/object/.aws/credentials`.
* Create `/home/object/codedeploy/get_credentials`:
```bash
#!/bin/bash

REGION=us-east-1
ROLE_ARN=...
FILE=/home/object/codedeploy/temporary-credentials

/usr/local/bin/get_sts_creds --region $REGION --role-arn $ROLE_ARN --file $FILE
```
* Add this to `crontab -e`: `0,15,30,45 * * * * /home/object/codedeploy/get_credentials`
* Run the above command, but add the flag `--print-session-arn`.
* Add this to `/etc/codedeploy-agent/conf/codedeploy.onpremises.yml`:
```yml
---
iam_session_arn: ...
aws_credentials_file: /home/object/codedeploy/temporary-credentials
region: us-east-1
```
* Run this somewhere with AWS power user permissions: `aws deploy register-on-premises-instance --instance-name objectobject-ca --iam-session-arn ...`
* Edit `/etc/codedeploy-agent/conf/codedeployagent.yml`, add this line:
```yml
:deploy_control_endpoint: 'https://codedeploy-commands.us-east-1.amazonaws.com'
```

## Dozzle user config

```yml
users:
  object:
    name: "[object Object]"
    password: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8  # sha256 of "password"
    email: object@objectobject.ca
```
