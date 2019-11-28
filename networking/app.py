#!/usr/bin/env python3
import os
from aws_cdk import core

from stacks.networking_stack import NetworkingStack
from stacks.routing_stack import RoutingStack
from stacks.ec2_stack import EC2Stack


app = core.App()

netStack = NetworkingStack(app, "networking-stack", env={
    'account': os.environ['CDK_DEFAULT_ACCOUNT'],
    'region': os.environ['CDK_DEFAULT_REGION']
})

routeStack = RoutingStack(app, id="routing-stack", nw_stack=netStack, env={
    'account': os.environ['CDK_DEFAULT_ACCOUNT'],
    'region': os.environ['CDK_DEFAULT_REGION']
  })

ec2Stack = EC2Stack(app, id="instance-stack", nw_stack=netStack, env={
    'account': os.environ['CDK_DEFAULT_ACCOUNT'],
    'region': os.environ['CDK_DEFAULT_REGION']
  })

routeStack.add_dependency(netStack)
ec2Stack.add_dependency(routeStack)

app.synth()
