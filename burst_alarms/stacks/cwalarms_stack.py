from aws_cdk import (
    core,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_sns as _sns
)

SNS_TOPIC_NAME = "PerformanceMonitoring"

class AlarmStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eventTargets = []

        policyStatement = _iam.PolicyStatement(
            resources=['*'],
            actions=[
                "cloudwatch:PutMetricAlarm",
                "cloudwatch:ListMetrics",
                "cloudwatch:DeleteAlarms",
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes"
            ],
            effect=_iam.Effect.ALLOW
        )

        sns_topic = _sns.Topic(self, id=SNS_TOPIC_NAME, topic_name=SNS_TOPIC_NAME)

        eventHandler = _lambda.Function(
            self, 'BurstCreditAlarms',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            handler='burst_alarms.handler',
            environment={"sns_topic": sns_topic.topic_arn}
        )
        eventHandler.add_to_role_policy(policyStatement)

        eventTargets.append(_targets.LambdaFunction(handler=eventHandler))

        pattern = _events.EventPattern(
            source=['aws.ec2'],
            detail_type=[ "AWS API Call via CloudTrail"],
            detail={
                "eventSource": [
                  "ec2.amazonaws.com"
                ],
                "eventName": [
                    "RunInstances",
                    "TerminateInstances",
                    "CreateVolume",
                    "DeleteVolume"
                ]
            }
        )

        _events.Rule(
            scope=self,
            id='BurstBalanceAlarmRule',
            description='Handles ec2:RunInstances, ec2:TerminateInstance, ec2:CreateVolume, ec2:DeleteVolume events',
            rule_name='BurstBalanceAlarmRule',
            event_pattern=pattern,
            targets=eventTargets
        )