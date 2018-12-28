#!/bin/env python

import boto3


def main(arn='', credentials={}):
    client = boto3.client('cloudtrail', **credentials)
    response = client.describe_trails(
        includeShadowTrails=True
    )

    if len(response['trailList']) == 0:
        return ["no cloudtrail"]
    else:
        return ["%s %s %s %s" % (
            trail['S3BucketName'],
            trail['IsMultiRegionTrail'],
            trail['SnsTopicARN'] if 'SnsTopicARN' in trail else 'no-sns-topic',
            trail['HomeRegion']) for trail in response['trailList']]


if __name__ == "__main__":
    print(main())
