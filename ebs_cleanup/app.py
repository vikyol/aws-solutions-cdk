#!/usr/bin/env python3

from aws_cdk import core

from ebs_cleanup.ebs_cleanup_stack import EbsCleanupStack


app = core.App()

EbsCleanupStack(app, "ebs-cleanup",
                env={'region': 'eu-central-1'},
                tags={
                    "CostCenter": "",
                    "Project": "",
                    "Owner": ""
                }
)

app.synth()
