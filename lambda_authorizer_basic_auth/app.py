"""
Simple authorization lambda
"""
from __future__ import print_function

import os
import re
import json
import base64

import boto3

def lambda_handler(event, context):
	print(json.dumps(event,indent=2))
	return"Hello World"
    																														  
																																						  
