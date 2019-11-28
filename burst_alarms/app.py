#!/usr/bin/env python3

from aws_cdk import core

from stacks.cwalarms_stack import AlarmStack


app = core.App()
AlarmStack(app,
           "burst_alarms_stack",
            env={'region': 'eu-central-1'},
            tags={
                "CostCenter": "",
                "Project": "",
                "Owner": ""
            }
)

app.synth()
