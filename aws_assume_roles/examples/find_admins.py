#!/bin/env python

import boto3
import datetime

# https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#genref-aws-service-namespaces
# This is an AWS product that I'm assuming no user has explicitly granted in
# an IAM policy. If a user has a policy granting them access to SUPER_ESOTERIC_AWS_NAMESPACE
# service, they're likely admins with *:* permissions
SUPER_ESOTERIC_AWS_NAMESPACE = 'mediapackage'


def get_paginated_results(product, action, key, credentials, args=None):
    args = {} if args is None else args
    return [y for sublist in [x[key] for x in boto3.client(product, **credentials).get_paginator(action).paginate(**args)] for y in sublist]


def main(arn='', credentials=None):
    """Get all IAM users with *:* permissions"""
    credentials = {} if credentials is None else credentials
    client = boto3.client('iam', **credentials)
    users = get_paginated_results('iam', 'list_users', 'Users', credentials)
    admins = []
    for user in users:
        response = client.list_policies_granting_service_access(
            Arn=user['Arn'],
            ServiceNamespaces=[SUPER_ESOTERIC_AWS_NAMESPACE]
        )
        if len(response['PoliciesGrantingServiceAccess'][0]['Policies']) > 0:
            last_used = user.get('PasswordLastUsed', datetime.datetime.utcfromtimestamp(0))
            admins.append((user['UserName'], str(last_used)))

    return admins


if __name__ == "__main__":
    print(main())
