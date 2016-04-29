aws_assume_roles Python module
==============================

Iterate over a set of AWS IAM roles and call an arbitrary method with each
role.

::

    aws_assume_roles --profile myawsprofilename examples.find_githubio_dns_records.main arnlist.txt

aws_assume_role bash script
===========================

Generate temporary credentials for an assumed role, save those ephemeral
credentials in the awscli config and set the alias of ``aaws`` to use this new
ephemeral awscli profile


Usage
-----
::

    Usage : . /home/gene/bin/aws_assume_role ROLE_ARN [PARENT_PROFILE_NAME]
            ^--- Note that this script must be sourced not executed

    Examples
      . /home/gene/bin/aws_assume_role arn:aws:iam::123456789012:role/ExampleRole
      aaws ec2 describe-instances
    or
      . /home/gene/bin/aws_assume_role arn:aws:iam::234567890123:role/ExampleRole staging
      aaws --region us-west-2 ec2 describe-instances