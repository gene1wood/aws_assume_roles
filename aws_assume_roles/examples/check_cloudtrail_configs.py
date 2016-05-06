#!/bin/env python

import boto3

def main(arn, credentials={}):
    client = boto3.client('cloudtrail', **credentials)
    response = client.describe_trails(
        includeShadowTrails=True
    )
    if len(response['trailList']) == 0:
        return "no cloudtrail"
    else:
        for trail in response['trailList']:
            return "%s %s" % (trail['S3BucketName'],
                              trail['IsMultiRegionTrail'])
