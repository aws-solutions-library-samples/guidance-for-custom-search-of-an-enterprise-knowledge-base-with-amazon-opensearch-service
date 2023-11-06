# Welcome to your CDK Python project!

0. Precondition
Please make sure you have over 14 GB memory and Python 3 and npm installed on your environment. Linux or Mac OS preferred.

If there's no npm, install via nvm:
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
```
Note the v0.39.3 is just an example, download your preferred version.Then close and reopen terminal, then

```
nvm install v16.15.1
```
or
```
nvm install node
```


1. Change directory to ./deployment folder
```
cd ./deployment
```


2. Install AWS CDK
```
npm install -g aws-cdk
```


3. Bootstrap the CDK to provision all the infrastructure needed for the CDK to make changes to your AWS account

```
pip3 install -r requirements.txt
```
(precondition: you have installed pip via "sudo apt install python3-pip")

export your account configuration to the environment
```
export AWS_ACCOUNT_ID=XXXXXXXXXXXX
export AWS_REGION=xx-xx-x
export AWS_ACCESS_KEY_ID=XXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXX
```
```
cdk bootstrap aws://[your-account-id]/[your-region]
```
you can install the required dependencies.


4. Deploy stacks Settings in cdk.json
(1) Configurate which function need to be deployed , pls open cdk.json in the deployment folder path, and modify the "selection" value according to your needs
Default is set as below:
```
    "selection":["knn_faq","feedback","post_selection","xgb_train","knn_doc"]
```
(2) You can also choose to deploy SageMaker endpoint by notebook or by python function.  pls open cdk.json in the deployment folder path, and modify the " "notebookDeployment"" value . Default is set as below:
```
    "notebookDeployment":true
```
(3) And also you can customize the DynamoDB table name in "table_name", and replace the default value.

(4) There are extension function as well for the solution. For example, if you want to deploy Amazon Lex bot powered by LLM, please change "nobot" to "bot" in "extension" field of "cdk.json" 
To configure a web UI for Lex bot, please create CloudFormation template in  "Getting Started" session in https://github.com/aws-samples/aws-lex-web-ui

Amazon Lex supported region:
Africa (Cape Town)
Europe (London)
Europe (Ireland)
Asia Pacific (Seoul)
Asia Pacific (Tokyo)
Canada (Central)
Asia Pacific (Singapore)
Asia Pacific (Sydney)
Europe (Frankfurt)
US East (N. Virginia)
US West (Oregon)


5. Below command will validate the environment and generate CloudFormation.json 
```
cdk synth
```
If everything is good, then
```
cdk deploy --all  --no-roll-back --require-approval never
```
6. The CDK deployment will provide 3 CloudFormation stacks with relevant resouces like Lambda, API Gateway, OpenSearch instance and SageMaker notebook etc.

7. Login with Secret Manager account and password in OpenSearch. Finish the settings with manual part inside
8. Open Sagemaker Jyputerlab instance and the repositories will be automatically downloaded into the environment, play with relevant notebook scripts to deploy Sagemaker endpoint.For notebook setup, please refer the guideline named with "DeployGuide-LLM&Search-V2.pdf" in the root directory

### Clean Up
When you don't need the environment and want to clean it up, run:

```
$ cdk destroy --all
```
Then resources which are not created by cdk, need to manually clean it up. Like SageMaker endpoints,endpoint configurations,models, pls go to AWS console SageMaker page and delete resources under the "Inference" part.

### Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

 for cdk developer guideline please refer: https://docs.aws.amazon.com/cdk/api/v2/python/index.html 

### Trouble Shooting

 | Problem                 |          Countermeasure    |
| ------------------------ | -------------------------- |
| In China the LLM model is too slow for deployment  due to network issue         | Under the Jupyter notebook LLM_Model folder, there's "code" and requirements.txt file, add China source for the dependency lib, e.g. put "-i https://pypi.tuna.tsinghua.edu.cn/simple" in the first line of the requirements.txt file                                |
| CORS error for China API Gateway endpoint accessing | Need to contact responsible AWS account team to query about how to open the 443/80/8080 port by legal requirement |


