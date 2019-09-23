
# Automated Burst Credit Alarms

This project creates necessary resources to automate the creation and deletion of
CPU credit balance and EBS burst credit alarms.

To create alarms for the existing instances, `tools/create_alarms.py` should be run.
This script iterates through the instances and creates an alarm per instance. It also
creates alarms for the attached EBS volumes.

The CDK project creates a CloudWatch Event Rule to keep track of certain Cloudtrail logs. 
CloudWatch Events triggers a Lambda function for these event:

 - ec2:RunInstances
 - ec2:TerminateInstances
 - ec2:CreateVolume
 - ec2:DeleteVolume
 
The Lambda function adds or removes alarms based on the API calls logged by CloudTrail. It uses the following API calls:
- CloudWatch:PutMetricAlarm
- CloudWatch:DeleteAlarms

The corresponding alarm is raised when:
CpuCreditBalance of an EC2 instance drops down to 0 for two consecutive data points and
BurstBalance of an EBS volume drops below 2% of its burst bucket.

An SNS topic is created by CDK. The default topic name *PerformanceMonitoring* can be
configured by updating *SNS_TOPIC_NAME* variable in ```cwalarms_stack```. A notification
message is sent to this topic whenever an alarm is raised. Subscribe to this topic to
receive the notifications. 

### AWS CDK
The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

# Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
