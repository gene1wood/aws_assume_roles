#!/bin/env python

import boto3


def main(arn='', credentials={}):
    result = []
    ec2c = boto3.client('ec2', **credentials)
    regions = [x['RegionName'] for x in ec2c.describe_regions()['Regions']]
    for region in regions:
        client = boto3.client('ec2', region_name=region, **credentials)
        paginator = client.get_paginator('describe_instances')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    result.append({
                        'Region': region,
                        'InstanceId': instance['InstanceId'],
                        'Tags': dict([(x['Key'], x['Value']) for
                                      x in (instance['Tags'] if 'Tags' in
                                      instance else [])])})
    return result


if __name__ == "__main__":
    print(main())
