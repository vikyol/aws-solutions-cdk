from aws_cdk import (
    core,
    aws_ec2 as _ec2
)



class RoutingStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, nw_stack: core.Stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)



        tgwRt = _ec2.CfnTransitGatewayRouteTable(
            self,
            id='TgwRt',
            transit_gateway_id=nw_stack.tgw.ref,
            tags=[core.CfnTag(key='Name', value='TGW-Nat-Rt')]
        )

        _ec2.CfnTransitGatewayRouteTablePropagation(
            self,
            id='tgw-natvpc-propagation',
            transit_gateway_route_table_id=tgwRt.ref,
            transit_gateway_attachment_id=nw_stack.tgw_nat_attachment.ref
        )

        _ec2.CfnTransitGatewayRouteTableAssociation(
            self,
            id='tgw-natvpc-rt-association',
            transit_gateway_route_table_id=tgwRt.ref,
            transit_gateway_attachment_id=nw_stack.tgw_nat_attachment.ref
        )

        _ec2.CfnTransitGatewayRouteTablePropagation(
            self,
            id='tgw-appvpc-propagation',
            transit_gateway_route_table_id=tgwRt.ref,
            transit_gateway_attachment_id=nw_stack.tgw_app_attachment.ref
        )

        _ec2.CfnTransitGatewayRouteTableAssociation(
            self,
            id='tgw-appvpc-rt-association',
            transit_gateway_route_table_id=tgwRt.ref,
            transit_gateway_attachment_id=nw_stack.tgw_app_attachment.ref
        )

        # TGW Routing
        # All traffic is routed to NAT GW VPC
        _ec2.CfnTransitGatewayRoute(
            self,
            id='tgw-nat-route',
            transit_gateway_route_table_id=tgwRt.ref,
            destination_cidr_block='0.0.0.0/0',
            transit_gateway_attachment_id=nw_stack.tgw_nat_attachment.ref
        )

        for subnet in nw_stack.app_vpc.isolated_subnets:
            _ec2.CfnRoute(
                self,
                id='app-vpc-route-all-tgw',
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block='0.0.0.0/0',
                transit_gateway_id=nw_stack.tgw.ref
            )

        for subnet in nw_stack.nat_vpc.public_subnets:
            _ec2.CfnRoute(
                self,
                id='nat-vpc-route-to-app',
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=nw_stack.app_vpc.vpc_cidr_block,
                transit_gateway_id=nw_stack.tgw.ref
            )