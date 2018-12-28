#!/bin/env python

import boto3


def get_paginated_results(product, action, key, region_name, credentials):
    return [y for sublist in [x[key] for x in boto3.client(product, region_name=region_name, **credentials).get_paginator(action).paginate()] for y in sublist]


def main(arn='', credentials={}):
    """Count the number of CloudFormation stacks in each region"""
    result = {}
    regions = boto3.session.Session().get_available_regions('cloudformation')
    for region in regions:
        stacks = get_paginated_results('cloudformation', 'list_stacks', 'StackSummaries', region, credentials)
        result[region] = len(stacks)
    return result


if __name__ == "__main__":
    print(main())
