#!/usr/bin/env python

import boto3
import logging

logging.basicConfig(level=logging.INFO)

GITHUBIO_IPS = ['192.30.252.153',
                '192.30.252.154']
GITHUBIO_SUFFIX = '.github.io.'


def main(arn, credentials={}):
    client = boto3.client('route53', **credentials)
    results = []
    hosted_zone_ids = []

    paginator = client.get_paginator('list_hosted_zones')
    response_iterator = paginator.paginate()

    for page in response_iterator:
        hosted_zone_ids.extend([x['Id'] for x in page['HostedZones']])

    for hosted_zone_id in hosted_zone_ids:
        paginator = client.get_paginator('list_resource_record_sets')
        response_iterator = paginator.paginate(
            HostedZoneId=hosted_zone_id
        )
        for page in response_iterator:
            if 'ResourceRecordSets' not in page:
                logging.debug("'ResourceRecordSets' not found in %s" % page)
                raise Exception()
            for record in page['ResourceRecordSets']:
                logging.info('Checking %s' % record['Name'])
                if record['Type'] == 'CNAME':
                    if 'ResourceRecords' not in record:
                        logging.debug("'ResourceRecords' not found in %s" %
                                      record)
                        raise Exception()
                    for value in [x['Value']
                                  for x
                                  in record['ResourceRecords']]:
                        if value.endswith(GITHUBIO_SUFFIX):
                            results.append({'HostedZoneId': hosted_zone_id,
                                            'Name': record['Name'],
                                            'Type': record['Type'],
                                            'Value': value})
                elif record['Type'] == 'A':
                    if 'ResourceRecords' not in record:
                        logging.debug("'ResourceRecords' not found in %s" %
                                      record)
                        continue
                    for value in [x['Value']
                                  for x
                                  in record['ResourceRecords']]:
                        if value in GITHUBIO_IPS:
                            results.append({'HostedZoneId': hosted_zone_id,
                                            'Name': record['Name'],
                                            'Type': record['Type'],
                                            'Value': value})

    return results
