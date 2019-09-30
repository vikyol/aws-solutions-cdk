# creates a test instance in the private of subnet of the app_vpc.

from aws_cdk import (
    core,
    aws_ec2 as _ec2
)


class EC2Stack(core.Stack):
    SSH_IP = '10.0.0.0/8'
    SSH_PORT = 22
    AMI_ID=''

    def __init__(self, scope: core.Construct, id: str, nw_stack: core.Stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ec2_sg = _ec2.SecurityGroup(
            self,
            id='test-ec2-instance-sg',
            vpc=nw_stack.app_vpc
        )

        ec2_sg.add_ingress_rule(
            peer=_ec2.Peer.prefix_list(EC2Stack.SSH_IP),
            connection=_ec2.Port(protocol=_ec2.Protocol.TCP, string_representation="tcp_22", from_port=EC2Stack.SSH_PORT, to_port=EC2Stack.SSH_PORT),
            description='Allow SSH access from SSH_IP'
        )

        _ec2.Instance(
            self,
            id='tgw_poc_instance',
            instance_type=_ec2.InstanceType('t3.micro'),
            machine_image=_ec2.AmazonLinuxImage(),
            key_name='tgw_test',
            security_group=ec2_sg,
            instance_name='tgw_nat_test_instance',
            vpc=nw_stack.app_vpc,
            vpc_subnets=nw_stack.app_vpc.select_subnets(subnet_type=_ec2.SubnetType.ISOLATED)
        )

