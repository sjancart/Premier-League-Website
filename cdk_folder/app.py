#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_folder.cdk_folder_stack import CdkFolderStack


app = cdk.App()
CdkFolderStack(app, "CdkFolderStack")

app.synth()
