from typing import List, Any

import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Creates EC2 CPU credit balance and EBS volume burst balance alarms.
def handler(event, context) -> bool:
    instance_ids = []

    try:
        detail = event['detail']
        event_name = detail['eventName']

        if not detail['responseElements']:
            logger.warning('No responseElements found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        ec2 = boto3.resource('ec2')

        if event_name == 'CreateVolume':
            volume_id: str = detail['responseElements']['volume_id']
            logger.info('Create an alarm for ' + volume_id)
            create_ebs_alarm(volume_id)

        elif event_name == 'DeleteVolume':
            volume_id: str = detail['requestParameters']['volume_id']
            logger.info('Delete the alarm for ' + volume_id)
            delete_ebs_alarm(volume_id)

        elif event_name == 'RunInstances' or event_name == 'TerminateInstances':
            volume_ids: List[Any] = []
            items = detail['responseElements']['instancesSet']['items']
            for item in items:
                instance_ids.append(item['instanceId'])

            logger.debug('number of instances: ' + str(len(instance_ids)))

            # Find the volumes attached to the instances
            for instance in ec2.instances.filter(InstanceIds=instance_ids):
                for vol in instance.volumes.all():
                    volume_ids.append({'id': vol.id, 'size': vol.size})

            if len(instance_ids) > 0:
                for resourceId in instance_ids:
                    logger.info('Creating an alarm for instance ' + resourceId)
                    if event_name == 'RunInstances':
                        create_cpu_alarm(resourceId)
                    elif event_name == 'TerminateInstances':
                        delete_cpu_alarm(resourceId)

            if len(volume_ids) > 0:
                logger.info(volume_ids)
                for volume in volume_ids:
                    if event_name == 'RunInstances':
                        create_ebs_alarm(volume['id'])
                    elif event_name == 'TerminateInstances':
                        delete_ebs_alarm(volume['id'])

        else:
            logger.warning('Not supported action')
            return False

        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False


# Create an alarm to monitor CpuCreditBalance.
# Alarm triggers if the CPU credit balance is zero for two consecutive periods.
def create_cpu_alarm(instance_id) -> None:
    # Create CloudWatch client
    cw = boto3.client('cloudwatch')

    # Create alarm
    cw.put_metric_alarm(
        AlarmName=instance_id + '_CPUCreditBalanceCheck',
        ComparisonOperator='LessThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='CPUCreditBalance',
        Namespace='AWS/EC2',
        Period=300,
        Statistic='Minimum',
        Threshold=0,
        ActionsEnabled=True,
        AlarmActions=[os.environ['sns_topic']],
        AlarmDescription='Alarm when CPU Credit Balance drops down to 0',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ]
    )
    logger.info('Alarm: ' + instance_id + '_CPUCreditBalanceCheck created')


def delete_cpu_alarm(instance_id) -> None:
    # Create CloudWatch client
    cw = boto3.client('cloudwatch')

    cw.delete_alarms(
        AlarmNames=[
            instance_id + '_CPUCreditBalanceCheck'
        ]
    )
    logger.info('Alarm: ' + instance_id + '_CPUCreditBalanceCheck deleted')


# Create an alarm to monitor BurstBalance.
# Alarm triggers if the EBS burst balance is below 2% for two consecutive periods.
def create_ebs_alarm(volume_id) -> None:
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
        AlarmActions=[os.environ['sns_topic']],
        AlarmDescription='Alarm when BurstBalance is below 2',
        Dimensions=[
            {
                'Name': 'VolumeId',
                'Value': volume_id
            },
        ]
    )
    logger.info('Alarm: ' + volume_id + '_BurstBalance created')


def delete_ebs_alarm(volume_id) -> None:
    # Create CloudWatch client
    cw = boto3.client('cloudwatch')

    cw.delete_alarms(
        AlarmNames=[
            volume_id + '_BurstBalance'
        ]
    )
    logger.info('Alarm: ' + volume_id + '_BurstBalance deleted')
