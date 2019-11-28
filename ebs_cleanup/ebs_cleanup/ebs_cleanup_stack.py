from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_s3 as _s3
)

class EbsCleanupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eventTargets = []

        policyStatement = _iam.PolicyStatement(
            resources=['*'],
            actions=[
                "cloudtrail:LookupEvents",
                "ec2:DeleteVolume",
                "ec2:DescribeVolumes",
            ],
            effect=_iam.Effect.ALLOW,
        )

        eventHandler = _lambda.Function(
            self, 'EbsCleanup',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            handler='ebs_cleanup.handler',
            timeout=core.Duration.minutes(5)
        )
        eventHandler.add_to_role_policy(policyStatement)

        eventTargets.append(_targets.LambdaFunction(handler=eventHandler))

        # Schedule the cleanup function to run once a month
        schedule = _events.Schedule.rate(core.Duration.days(30))


        _events.Rule(
            scope=self,
            id='EbsCleanupRule',
            description='Cleanup detached volumes older than 30 days',
            rule_name='EbsCleanupRule',
            schedule=schedule,
            targets=eventTargets
        )