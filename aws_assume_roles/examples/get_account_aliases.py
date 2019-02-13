#!/bin/env python

import boto3


def main(arn='', credentials=None):
    """Get account aliases"""
    credentials = {} if credentials is None else credentials
    client = boto3.client('iam', **credentials)
    aliases = client.list_account_aliases()
    return aliases['AccountAliases']


if __name__ == "__main__":
    print(main())
