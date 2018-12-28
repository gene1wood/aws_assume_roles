#!/bin/env python

import boto3


def get_paginated_results(product, action, key, credentials={}, args={}):
    return [y for sublist in [x[key] for x in boto3.client(product, **credentials).get_paginator(action).paginate(**args)] for y in sublist]


def simulate_policy(arn, credentials):
    """Given an IAM user/role, determine if it has rights to iam:AssumeRole"""
    args = {'PolicySourceArn': arn,
            'ActionNames': ['iam:AssumeRole']}
    results = [
        "%s %s %s %s %s %s" % (
            arn,
            x['EvalActionName'],
            x['EvalResourceName'],
            x['EvalDecision'],
            x['MatchedStatements'],
            x['EvalDecisionDetails']) for x in
        get_paginated_results('iam', 'simulate_principal_policy',
                              'EvaluationResults', credentials, args)]
    return results


def main(arn='', credentials={}):
    """Determine which IAM users and roles can iam:AssumeRole"""
    results = []

    for user in get_paginated_results('iam', 'list_users', 'Users', credentials):
        results.extend(simulate_policy(user['Arn'], credentials))

    for role in get_paginated_results('iam', 'list_roles', 'Roles', credentials):
        results.extend(simulate_policy(role['Arn'], credentials))

    return results


if __name__ == "__main__":
    print(main())
