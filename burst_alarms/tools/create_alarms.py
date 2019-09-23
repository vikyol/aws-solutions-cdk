import boto3
import logging

# Creates alarms for existing EC2 instances. This script finds all existing EC2 instances and their attached volumes
# and creates alarms accordingly.
# Export your AWS credentials as environment variables before running this script or set a default
# profile (~/.aws/credentials) using:
# export AWS_DEFAULT_PROFILE=<named_profile>

# Usage: python create_alarms.py

ec2 = boto3.resource('ec2')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set your SNS topic ARN to receive notifications
SNS_TOPIC = "arn:aws:sns:<region>:<account_id>:<topic_name>"


# Create an alarm to monitor CpuCreditBalance.
# Raise an alarm if the burst credit balance goes down to 0
def create_cpu_alarm(instance_id):
    alarm_name = instance_id + '_CPUCreditBalanceCheck'

    # Create CloudWatch client
    cw = boto3.client('cloudwatch')

    # Create a CPU Credit Balance alarm, triggers when the CPU balance is 0 in two consecutive periods
    cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='LessThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='CPUCreditBalance',
        Namespace='AWS/EC2',
        Period=300,
        Statistic='Minimum',
        Threshold=0,
        ActionsEnabled=True,
        AlarmActions=[SNS_TOPIC],
        AlarmDescription='Raise the alarm when CPU Credit Balance drops down to 0 for 2 consecutive periods',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ]
    )
    logger.info('Alarm: ' + instance_id + '_CPUCreditBalanceCheck created')


def create_ebs_alarm(volume_id):
    # Create CloudWatch client
    cw = boto3.client('cloudwatch')

    # Create alarm
    cw.put_metric_alarm(
        AlarmName=volume_id + '_BurstBalance',
        ComparisonOperator='LessThanThreshold',
        EvaluationPeriods=2,
        MetricName='BurstBalance',
        Namespace='AWS/EBS',
        Period=300,
        Statistic='Average',
        Threshold=2,
        ActionsEnabled=True,
        AlarmActions=[SNS_TOPIC],
        AlarmDescription='Alarm when BurstBalance is below 10% for 2 data points',
        Dimensions=[
            {
                'Name': 'VolumeId',
                'Value': volume_id
            },
        ]
    )
    logger.info('Alarm: ' + volume_id + '_BurstBalance created')


def alarm_exists(name) -> bool:
    cw = boto3.client('cloudwatch')
    rsp = cw.describe_alarms(AlarmNames=[name])

    return len(rsp['MetricAlarms']) > 0


if __name__ == '__main__':
    instances = ec2.instances.filter()
    # Check all existing instances and their volumes
    for instance in instances:
        print("Creating a CPU alarms for " + instance.id)
        create_cpu_alarm(instance.id)

        volumes = instance.volumes.all()

        for v in volumes:
            print(v.id + " of type " + v.volume_type)
            if v.volume_type == 'gp2':
                print("Enabling BurstBalance alarm for " + v.id)
                create_ebs_alarm(v.id)