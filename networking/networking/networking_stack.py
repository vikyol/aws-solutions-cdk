from aws_cdk import (
    core,
    aws_ec2 as _ec2
)


class NetworkingStack(core.Stack):
    app_vpc = None
    nat_vpc = None
    tgw = None
    tgw_nat_attachment = None

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.nat_vpc = _ec2.Vpc(
            self,
            id="nat_vpc",
            cidr="10.10.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=1,
            nat_gateways=1,
            subnet_configuration=[
                _ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='nat-public',
                    subnet_type=_ec2.SubnetType.PUBLIC
                ),
                _ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='nat-private',
                    subnet_type=_ec2.SubnetType.PRIVATE
                )
            ]
        )

        self.app_vpc = _ec2.Vpc(
            self,
            id="app_vpc",
            cidr="10.30.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=1,
            nat_gateways=0,
            subnet_configuration=[
                _ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='app-public1',
                    subnet_type=_ec2.SubnetType.PUBLIC
                ),
                _ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='app-private1',
                    subnet_type=_ec2.SubnetType.ISOLATED
                )
            ]
        )

        self.tgw = _ec2.CfnTransitGateway(
            self,
            id='tgw-test',
            amazon_side_asn=65520,
            auto_accept_shared_attachments="enable",
            default_route_table_association="enable",
            default_route_table_propagation="enable",
            tags=[core.CfnTag(key='Name', value='TGW-PoC')]
        )


        self.tgw_nat_attachment = _ec2.CfnTransitGatewayAttachment(
            self,
            id="tgw-natvpc",
            transit_gateway_id=self.tgw.ref,
            vpc_id=self.nat_vpc.vpc_id,
            subnet_ids=[subnet.subnet_id for subnet in self.nat_vpc.private_subnets]
        )

        self.tgw_app_attachment = _ec2.CfnTransitGatewayAttachment(
            self,
            id="tgw-appvpc",
            transit_gateway_id=self.tgw.ref,
            vpc_id=self.app_vpc.vpc_id,
            subnet_ids=[subnet.subnet_id for subnet in self.app_vpc.isolated_subnets]
        )
