#!/usr/bin/env python3

from aws_cdk import core

from networking.networking_stack import NetworkingStack


app = core.App()
NetworkingStack(app, "networking")

app.synth()
