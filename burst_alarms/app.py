#!/usr/bin/env python3

from aws_cdk import core

from stacks.cwalarms_stack import AlarmStack


app = core.App()
AlarmStack(app, "stacks")

app.synth()
