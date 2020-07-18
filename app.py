#!/usr/bin/env python3

from aws_cdk import core

from ts_www.ts_www_stack import TsWwwStack


app = core.App()
TsWwwStack(app, "ts-www")

app.synth()
