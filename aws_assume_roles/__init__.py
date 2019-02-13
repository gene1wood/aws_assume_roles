#!/usr/bin/env python

import argparse
import logging
import importlib
import os
import sys
import boto3
import functools
import json

if 'lru_cache' in functools.__dict__:
    # Python 3
    lru_cache = functools.lru_cache
else:
    # Python 2
    try:
        from functools32 import lru_cache
    except ImportError:
        # Make our own memoize decorator and assign it to lru_cache?
        raise Exception(
            "Unable to find lru_cache method in functools because "
            "this isn't Python 3 and unable to find functools32 module with "
            "backported lru_cache method")


def type_loglevel(level):
    try:
        result = getattr(logging, level.upper())
    except AttributeError:
        raise argparse.ArgumentTypeError(
            "'%s' is not a valid log level. Please use %s" %
            (level, [x
                     for x
                     in logging._levelNames.keys()
                     if isinstance(x, str)]))
    return result


def type_method(method):
    module_name = '.'.join(method.split('.')[:-1])
    method_name = '.'.join(method.split('.')[-1:])
    if len(module_name) == 0:
        raise argparse.ArgumentTypeError('%s is missing a module and method '
                                         'name')
    try:
        # Add the current working directory to the path
        sys.path.insert(0, os.getcwd())
        i = importlib.import_module(module_name)
    except ImportError:
        raise argparse.ArgumentTypeError('unable to find module %s' %
                                         module_name)
    try:
        result = getattr(i, method_name)
    except AttributeError:
        raise argparse.ArgumentTypeError(
            'unable to find method %s in module %s . found %s' %
            (method_name, module_name, dir(i)))
    return result


@lru_cache(maxsize=32)
def get_assumed_role(role_arn,
                     profile_name=None,
                     role_session_name='aws_assume_role',
                     policy=None):
    logging.debug("Connecting to sts")
    try:
        params = {} if profile_name is None else {'profile_name': profile_name}
        session = boto3.Session(**params)
        client_sts = session.client('sts')
    except Exception as e:
        logging.error("Unable to connect to sts with exception %s" % e)
        raise
    try:
        params = {'RoleArn': role_arn,
                  'RoleSessionName': role_session_name}
        if policy is not None:
            params['Policy'] = policy
        response = client_sts.assume_role(**params)
    except Exception as e:
        logging.error("Unable to assume role %s due to exception %s" %
                      (role_arn, e))
        return False
    credentials = {
        'aws_access_key_id': response['Credentials']['AccessKeyId'],
        'aws_secret_access_key': response['Credentials']['SecretAccessKey'],
        'aws_session_token': response['Credentials']['SessionToken']}
    return credentials


def get_args():
    parser = argparse.ArgumentParser(
        description='Iterate over a set of AWS IAM roles and call an '
                    'arbitrary method with each role')
    parser.add_argument(
        'method', type=type_method, help='a dot delimited method name')
    parser.add_argument(
        'arnfile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='a filename of a list of ARNs, one per line (default : stdin)')
    parser.add_argument('--profile', help='AWS credential profile name')
    parser.add_argument(
        '-l', '--loglevel', type=type_loglevel, default='INFO',
        help='Log level verbosity (default: INFO)')
    parser.add_argument(
        '--output', help='Filename to output to instead of stdout')
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    # Disable boto logging
    logging.getLogger('boto3').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)

    return args


def main():
    args = get_args()
    results = {}
    for line in args.arnfile.readlines():
        arn = line.split('#')[0].strip()
        if len(arn) == 0:
            continue
        credentials = get_assumed_role(role_arn=arn, profile_name=args.profile)
        if credentials:
            results[arn] = args.method(arn=arn, credentials=credentials)
        else:
            if 'errors' not in results:
                results['errors'] = []
            results['errors'].append('Unable to assume_role to %s' % arn)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=4)
            print('{} records collected for {}'.format(len(results[arn]), arn))

    if not args.output:
        print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()
