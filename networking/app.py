#!/usr/bin/env python3

from aws_cdk import core

from stacks.networking_stack import NetworkingStack
from stacks.routing_stack import RoutingStack
from stacks.ec2_stack import EC2Stack


app = core.App()
netStack = NetworkingStack(app, "networking")

routeStack = RoutingStack(app, id="routing", nw_stack=netStack)

ec2Stack = EC2Stack(app, id="instance", nw_stack=netStack)

routeStack.add_dependency(netStack)
ec2Stack.add_dependency(routeStack)

app.synth()
