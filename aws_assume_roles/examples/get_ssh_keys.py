#!/bin/env python

import boto3


def main(arn='', credentials={}):
    result = []
    regions = boto3.session.Session().get_available_regions('ec2')
    for region in regions:
        client = boto3.client('ec2', region_name=region, **credentials)
        response = client.describe_key_pairs()
        result.extend(
            ['%s (%s)' % (x['KeyName'], region) for x in response['KeyPairs']])

    return result


if __name__ == "__main__":
    print(main())
