#!/usr/bin/env python3

from aws_cdk import core

from stacks.autotags_stack import AutoTagsStack


app = core.App()
AutoTagsStack(app, "autotags")

app.synth()
