# objectobject.ca

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