#!/bin/bash

usage () {
  cat <<DOCUMENTATIONXX
Usage : . $0 ROLE_ARN [PARENT_PROFILE_NAME]
        ^--- Note that this script must be sourced not executed

This tool will generate temporary credentials for an assumed role, save
those ephemeral credentials in the awscli config and set the alias of
"aaws" to use this new ephemeral awscli profile

Examples
  . $0 arn:aws:iam::123456789012:role/ExampleRole
  aaws ec2 describe-instances
or
  . $0 arn:aws:iam::234567890123:role/ExampleRole staging
  aaws --region us-west-2 ec2 describe-instances


DOCUMENTATIONXX
}

if [ "$1" == "-h" -o "$1" == "--help" -o "$1" == "" ]; then
    usage
    exit 1
fi

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "You must source this script instead of running it. Try this instead : "
    echo ". $0 $*"
    echo ""
    usage
    exit 1
fi

role_arn=$1
parent_profile=$2
arn_array=(${role_arn//:/ })
account_id=${arn_array[3]}
profile_path=${arn_array[4]}
profile_name="ephemeral-${account_id}-${profile_path}-`date +%Y%m%d%H%M%S`"

session_name="${USER}-`hostname`-`date +%Y%m%d`"
if [ -n "$parent_profile" ]; then
    profile_argument="--profile $parent_profile"
fi
sts=( $(
    aws sts assume-role \
    ${profile_argument} \
    --role-arn "$role_arn" \
    --role-session-name "$session_name" \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text
) )

aws configure set aws_access_key_id ${sts[0]} --profile ${profile_name}
aws configure set aws_secret_access_key ${sts[1]} --profile ${profile_name}
aws configure set aws_session_token ${sts[2]} --profile ${profile_name}

alias aaws="aws --profile ${profile_name}"
alias aaws-${account_id}="aws --profile ${profile_name}"

if [[ $PS1 =~ \(AWS:[0-9]*\)[[:space:]](.*) ]]; then
    PS1="(AWS:$account_id) ${BASH_REMATCH[1]}"
else
    PS1="(AWS:$account_id) $PS1"
fi

