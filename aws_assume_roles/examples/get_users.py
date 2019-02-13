#!/bin/env python

import boto3
import datetime


def get_paginated_results(product, action, key, credentials, args=None):
    args = {} if args is None else args
    return [y for sublist in [x[key] for x in boto3.client(product, **credentials).get_paginator(action).paginate(**args)] for y in sublist]


def main(arn='', credentials=None):
    """Get users, the last time they logged in with a password and each of
    their API keys and the last time those keys were used

    :param arn:
    :param credentials:
    :return: A 3-tuple of
        IAM username
        the datetime that the password was last used for login
        a list of 2-tuples one for each API key with values of
            The access key id (public key)
            The datetime that the key was last used
    """
    credentials = {} if credentials is None else credentials

    client = boto3.client('iam', **credentials)
    result = []
    users = get_paginated_results('iam', 'list_users', 'Users', credentials)
    for user in users:
        last_used_password = user.get('PasswordLastUsed',
                                      datetime.datetime.utcfromtimestamp(0))
        access_keys = get_paginated_results(
            'iam', 'list_access_keys', 'AccessKeyMetadata', credentials,
            args={'UserName': user['UserName']})
        keys = []
        for access_key in access_keys:
            response = client.get_access_key_last_used(
                AccessKeyId=access_key['AccessKeyId']
            )
            last_used_access_key = response['AccessKeyLastUsed'].get(
                'LastUsedDate', datetime.datetime.utcfromtimestamp(0))
            keys.append((access_key['AccessKeyId'], str(last_used_access_key)))

        result.append((user['UserName'], str(last_used_password), keys))

    return result


if __name__ == "__main__":
    print(main())
