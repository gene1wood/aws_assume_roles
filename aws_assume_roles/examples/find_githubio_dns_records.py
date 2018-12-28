#!/usr/bin/env python

import boto3
import logging

logging.basicConfig(level=logging.INFO)

# https://help.github.com/articles/troubleshooting-custom-domains/
GITHUBIO_IPS = ['192.30.252.153',
                '192.30.252.154',
                '185.199.108.153',
                '185.199.109.153',
                '185.199.110.153',
                '185.199.111.153',
                '207.97.227.245',
                '204.232.175.78'
                ]
GITHUBIO_SUFFIX = '.github.io.'


def main(arn='', credentials={}):
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
                        continue  # Previously we raised an Exception here but I'm not sure why
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


if __name__ == "__main__":
    print(main())
