#!/usr/bin/env python3

from aws_cdk import core

from ts_www.ts_www_stack import TsWwwStack

#aws_env = core.Environment(account=aws_account,region=aws_region)

aws_env = core.Environment(account = "925270102238", region="us-east-1")

app = core.App()
TsWwwStack(app, "ts-www", env=aws_env , domain_name="tsaws.com")

app.synth()
