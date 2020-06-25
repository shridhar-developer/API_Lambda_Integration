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

    # Ensure the incoming Lambda event is for a request authorizer
    if event['type'] != 'REQUEST':
        raise Exception('Unauthorized')

    try:
        
        principalId = event['requestContext']['accountId']

        tmp = event['methodArn'].split(':')
        apiGatewayArnTmp = tmp[5].split('/')
        awsAccountId = tmp[4]

        policy = AuthPolicy(principalId, awsAccountId)
        policy.restApiId = apiGatewayArnTmp[0]
        policy.region = tmp[3]
        policy.stage = apiGatewayArnTmp[1]

        # Get authorization header in lowercase
        authorization_header = {k.lower(): v for k, v in event['headers'].items() if k.lower() == 'authorization'}


        # Get the username:password hash from the authorization header
        username_password_hash = authorization_header['authorization'].split()[1]

        # Decode username_password_hash and get username
        username = base64.standard_b64decode(username_password_hash).split(':')[0]

        policy.allowMethod(event['requestContext']['httpMethod'], event['path'])

        # Finally, build the policy
        authResponse = policy.build()

        return authResponse
    except Exception:
        raise Exception('Unauthorized')


class HttpVerb:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    ALL = "*"


class AuthPolicy(object):
    awsAccountId = ""
    
    principalId = ""
   
    version = "2012-10-17"
    
    pathRegex = "^[/.a-zA-Z0-9-\*]+$"
  
                                                                                                                                    allowMethods = []


    restApiId = "*"
    
    region = "*"
    
    stage = "*"
    

    def __init__(self, principal, awsAccountId):
        self.awsAccountId = awsAccountId
        self.principalId = principal
        self.allowMethods = []
        self.denyMethods = []

    def _addMethod(self, effect, verb, resource, conditions):

        if verb != "*" and not hasattr(HttpVerb, verb):
            raise NameError("Invalid HTTP verb " + verb + ". Allowed verbs in HttpVerb class")
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError("Invalid resource path: " + resource + ". Path should match " + self.pathRegex)

        if resource[:1] == "/":
            resource = resource[1:]

        resourceArn = ("arn:aws:execute-api:" +
            self.region + ":" +
            self.awsAccountId + ":" +
            self.restApiId + "/" +
            self.stage + "/" +
            verb + "/" +
            resource)

        if effect.lower() == "allow":
            self.allowMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })
        elif effect.lower() == "deny":
            self.denyMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })

    def _getEmptyStatement(self, effect):

        statement = {
            'Action': 'execute-api:Invoke',
            'Effect': effect[:1].upper() + effect[1:].lower(),
            'Resource': []
        }

        return statement

    def _getStatementForEffect(self, effect, methods):

        statements = []

        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)

            for curMethod in methods:
                if curMethod['conditions'] is None or len(curMethod['conditions']) == 0:
                    statement['Resource'].append(curMethod['resourceArn'])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement['Resource'].append(curMethod['resourceArn'])
                    conditionalStatement['Condition'] = curMethod['conditions']
                    statements.append(conditionalStatement)

            statements.append(statement)

        return statements       																														  
																																						  