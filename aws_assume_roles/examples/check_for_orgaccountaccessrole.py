#!/bin/env python

import boto3
import datetime


def get_paginated_results(product, action, key, credentials={}, args=None):
    args = {} if args is None else args
    return [y for sublist in [x[key] for x in boto3.client(product, **credentials).get_paginator(action).paginate(**args)] for y in sublist]


def main(arn='', credentials={}):
    """Get OrganizationAccountAccessRole"""

    client = boto3.client('iam', **credentials)
    result=None
    try:
        response = client.get_role(RoleName='OrganizationAccountAccessRole')
        result = response['Role']['AssumeRolePolicyDocument']
    except:
        pass
    return result


if __name__ == "__main__":
    print(main())
