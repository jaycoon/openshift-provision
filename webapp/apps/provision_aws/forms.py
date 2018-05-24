import logging

import boto3
import botocore.exceptions
from django import forms


logger = logging.getLogger(__name__)


class AmazonWebServicesForm(forms.Form):
    aws_access_key_id = forms.CharField(
        label='AWS Access Key',
        required=True,
    )

    aws_secret_access_key = forms.CharField(
        label='AWS Secret Key',
        required=True,
    )

    aws_region = forms.ChoiceField(
        label='AWS Region',
        required=True,
        initial='us-east-1',
        choices=[
           ('us-east-1', 'us-east-1'),
           ('us-east-2', 'us-east-2'),
           ('us-west-1', 'us-west-1'),
           ('us-west-2', 'us-west-2'),
           ('ap-south-1', 'ap-south-1'),
           ('ap-southeast-1', 'ap-southeast-1'),
           ('ap-northeast-2', 'ap-northeast-2'),
           ('ap-northeast-3', 'ap-northeast-3'),
           ('ap-northeast-1', 'ap-northeast-1'),
           ('ap-southeast-2', 'ap-southeast-2'),
           ('ca-central-1', 'ca-central-1'),
           ('cn-north-1', 'cn-north-1'),
           ('eu-central-1', 'eu-central-1'),
           ('eu-west-1', 'eu-west-1'),
           ('eu-west-2', 'eu-west-2'),
           ('eu-west-3', 'eu-west-3'),
           ('sa-east-1', 'sa-east-1'),
        ],
    )

    def clean(self):
        cleaned_data = super().clean()

        aws_access_key_id = cleaned_data.get('aws_access_key_id')
        aws_secret_access_key = cleaned_data.get('aws_secret_access_key')
        aws_region = cleaned_data.get('aws_region')

        sts = boto3.client('sts',
                           aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key,
                           region_name=aws_region)

        try:
            sts.get_session_token()
        except botocore.exceptions.ClientError:
            logger.exception('Invalid AWs credentials')
            raise forms.ValidationError(
                'Invalid AWS credentials. Ensure that "{}" and "{}" are valid.'.format(
                    self.fields['aws_access_key_id'].label,
                    self.fields['aws_secret_access_key'].label,
                )
            )


class AmazonWebServicesDetailsForm(forms.Form):
    cluster_name = forms.CharField(
        label='Cluster Name',
        required=True,
    )

    cluster_type = forms.ChoiceField(
        label='Cluster Type',
        required=True,
        initial='multi',
        choices=[
            ('multi', '[multi] 1 master, 1 infra, 2 app'),
        ],
    )

    openshift_version = forms.ChoiceField(
        label='Openshift Version',
        required=True,
        initial='3.9',
        choices=[
            ('3.9', 'OpenShift 3.9'),
        ],
    )

    # TODO: Rename to openshift_base_domain
    # TODO: Validate that it is a subdomain of the hosted zone
    openshift_base_domain = forms.CharField(
        label='OpenShift Base Domain',
        required=True,
    )

    # TODO: Check if user can see Cloud Access AMIs and make this choice for them
    ec2_ami_type = forms.ChoiceField(
        label='EC2 AMI Type',
        required=True,
        initial='hourly',
        choices=[
            ('hourly', 'Hourly'),
            ('cloud_access', 'Cloud Access'),
        ],
    )

    ec2_key_name = forms.ChoiceField(
        label='EC2 Key Pair',
        required=True,
        choices=[],
    )

    # TODO: Have user mount SSH keys into container and discover list of keys
    ec2_key_file = forms.CharField(
        label='EC2 Private Key',
        required=True,
    )

    route53_hosted_zone_id = forms.ChoiceField(
        label='Route53 Hosted Zone',
        required=True,
        choices=[],
    )

    rhsm_username = forms.CharField(
        label='RHSM Username',
        required=True,
    )

    rhsm_password = forms.CharField(
        label='RHSM Password',
        required=True,
        widget=forms.PasswordInput,
    )

    rhsm_pool = forms.CharField(
        label='RHSM Pool ID',
        required=True
    )

    def __init__(self, aws_credentials, *args, **kwargs):
        super(AmazonWebServicesDetailsForm, self).__init__(*args, **kwargs)

        self.boto3_session = boto3.Session(
            aws_access_key_id=aws_credentials.get('aws_access_key_id'),
            aws_secret_access_key=aws_credentials.get('aws_secret_access_key'),
            region_name=aws_credentials.get('aws_region'),
        )

        self.fields['ec2_key_name'].choices = self._choices_ec2_key_name()
        self.fields['route53_hosted_zone_id'].choices = self._choices_route53_hosted_zone_id()

    @classmethod
    def _generate_field_choices(cls, choices, include_empty_choice=False):
        field_choices = []
        for choice in choices:
            field_choices.append((choice, choice))

        # Sort the field choices
        field_choices = sorted(field_choices)

        # Include an empty choice if specified
        if include_empty_choice:
            field_choices.insert(0, ('', ''))

        return field_choices

    def _choices_ec2_key_name(self):
        ec2 = self.boto3_session.resource('ec2')

        choices = [key_pair.name for key_pair in ec2.key_pairs.all()]
        return self._generate_field_choices(choices, include_empty_choice=True)

    def _choices_route53_hosted_zone_id(self):
        route53 = self.boto3_session.client('route53')

        choices = [
            ('', ''),
        ]
        hosted_zones = route53.list_hosted_zones().get('HostedZones', [])
        for hosted_zone in hosted_zones:
            hosted_zone_name = hosted_zone.get('Name', '')
            hosted_zone_id = hosted_zone.get('Id', '').replace('hostedzone', '').replace('/', '')
            choices.append((hosted_zone_id, '[{}] {}'.format(hosted_zone_id, hosted_zone_name)))

        print(choices)

        return choices
