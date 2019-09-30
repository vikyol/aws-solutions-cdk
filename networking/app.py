#!/usr/bin/env python3

from aws_cdk import core

from networking.networking_stack import NetworkingStack
from networking.routing_stack import RoutingStack
from networking.ec2_stack import EC2Stack


app = core.App()
netStack = NetworkingStack(app, "networking")

#props = core.StackProps(tgw=netStack.tgw, appVpc=netStack.app_vpc, nat_vpc=netStack.nat_vpc)

routeStack = RoutingStack(app, id="routing", nw_stack=netStack)

ec2Stack = EC2Stack(app, id="instance", nw_stack=netStack)

routeStack.add_dependency(netStack)
ec2Stack.add_dependency(netStack)


app.synth()