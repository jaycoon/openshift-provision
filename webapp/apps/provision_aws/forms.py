import glob
import logging
import os

import boto3
import botocore.exceptions
from django import forms
from django.conf import settings

from .models import AWSAccessKey, AWSCluster


logger = logging.getLogger(__name__)


class AmazonWebServicesDetailsForm(forms.Form):
    cluster_name = forms.CharField(
        label='Cluster Name',
        required=True,
        help_text='This value will be in your DNS entries and should conform to valid DNS characters.'
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

    # TODO: Check if user can see Cloud Access AMIs and make this choice for them
    ec2_ami_type = forms.ChoiceField(
        label='EC2 AMI Type',
        required=True,
        initial='hourly',
        choices=[
            ('hourly', 'Hourly'),
            ('cloud_access', 'Cloud Access'),
        ],
        help_text=('If you have Cloud Access enabled, choose <strong>Cloud Access</strong>. Otherwise, '
                   'choose <strong>Hourly</strong>.')
    )

    ec2_key_name = forms.ChoiceField(
        label='EC2 Key Pair',
        required=True,
        choices=[],
    )

    # TODO: Have user mount SSH keys into container and discover list of keys
    ec2_key_file = forms.ChoiceField(
        label='EC2 Private Key',
        required=True,
        choices=[],
        help_text='Select the private key that matches the EC2 Key Pair selected above.'
    )

    route53_hosted_zone_id = forms.ChoiceField(
        label='Route53 Hosted Zone',
        required=True,
        choices=[],
    )

    # TODO: Rename to openshift_base_domain
    # TODO: Validate that it is a subdomain of the hosted zone
    openshift_base_domain = forms.CharField(
        label='OpenShift Base Domain',
        required=True,
        help_text=('The base domain for your cluster. The value should match or be a subdomain of the '
                   'Route53 Hosted Zone.'
                   '<br><br>'
                   'Example: If you set this to <code>example.com</code>, a DNS entry '
                   'of <code>&lt;cluster_name&gt;.example.com</code> will be created.')
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
        self.fields['ec2_key_file'].choices = self._choices_ec2_key_file()

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

        return choices

    def _choices_ec2_key_file(self):
        ssh_keys_glob = glob.glob(os.path.join(settings.SSH_KEYS_DIR, '**/*'), recursive=True)

        choices = [x for x in ssh_keys_glob if os.path.isfile(x)]
        return self._generate_field_choices(choices, include_empty_choice=True)


class AWSAccessKeyForm(forms.ModelForm):
    class Meta:
        model = AWSAccessKey
        fields = '__all__'

    def clean(self):
        super(AWSAccessKeyForm, self).clean()

        cleaned_data = super().clean()

        access_key = cleaned_data['access_key']
        secret_key = cleaned_data['secret_key']

        sts = boto3.client('sts',
                           aws_access_key_id=access_key,
                           aws_secret_access_key=secret_key,
                           region_name='us-east-1')

        try:
            sts.get_session_token()
        except botocore.exceptions.ClientError:
            logger.exception('Invalid AWs credentials')
            raise forms.ValidationError(
                'Unable to connect using the provided AWS credentials. Verify that "{}" and "{}" are correct.'.format(
                    self.fields['access_key'].label,
                    self.fields['secret_key'].label,
                )
            )


class AWSClusterForm(forms.ModelForm):
    class Meta:
        model = AWSCluster
        fields = '__all__'
        widgets = {
            'rhsm_password': forms.PasswordInput,
        }

    # def __init__(self, aws_credentials, *args, **kwargs):
    #     super(AWSClusterForm, self).__init__(*args, **kwargs)
    #
    #     self.boto3_session = boto3.Session(
    #         aws_access_key_id=aws_credentials.get('aws_access_key_id'),
    #         aws_secret_access_key=aws_credentials.get('aws_secret_access_key'),
    #         region_name=aws_credentials.get('aws_region'),
    #     )
    #
    #     self.fields['ec2_key_name'].choices = self._choices_ec2_key_name()
    #     self.fields['route53_hosted_zone_id'].choices = self._choices_route53_hosted_zone_id()
    #     self.fields['ec2_key_file'].choices = self._choices_ec2_key_file()
    #
    # @classmethod
    # def _generate_field_choices(cls, choices, include_empty_choice=False):
    #     field_choices = []
    #     for choice in choices:
    #         field_choices.append((choice, choice))
    #
    #     # Sort the field choices
    #     field_choices = sorted(field_choices)
    #
    #     # Include an empty choice if specified
    #     if include_empty_choice:
    #         field_choices.insert(0, ('', ''))
    #
    #     return field_choices
    #
    # def _choices_ec2_key_name(self):
    #     ec2 = self.boto3_session.resource('ec2')
    #
    #     choices = [key_pair.name for key_pair in ec2.key_pairs.all()]
    #     return self._generate_field_choices(choices, include_empty_choice=True)
    #
    # def _choices_route53_hosted_zone_id(self):
    #     route53 = self.boto3_session.client('route53')
    #
    #     choices = [
    #         ('', ''),
    #     ]
    #     hosted_zones = route53.list_hosted_zones().get('HostedZones', [])
    #     for hosted_zone in hosted_zones:
    #         hosted_zone_name = hosted_zone.get('Name', '')
    #         hosted_zone_id = hosted_zone.get('Id', '').replace('hostedzone', '').replace('/', '')
    #         choices.append((hosted_zone_id, '[{}] {}'.format(hosted_zone_id, hosted_zone_name)))
    #
    #     return choices
    #
    # def _choices_ec2_key_file(self):
    #     ssh_keys_glob = glob.glob(os.path.join(settings.SSH_KEYS_DIR, '**/*'), recursive=True)
    #
    #     choices = [x for x in ssh_keys_glob if os.path.isfile(x)]
    #     return self._generate_field_choices(choices, include_empty_choice=True)
    #
    # def clean(self):
    #     super(AWSClusterForm, self).clean()
    #
    #     cleaned_data = super().clean()
    #
    #     access_key = cleaned_data['access_key']
    #     secret_key = cleaned_data['secret_key']
    #
    #     sts = boto3.client('sts',
    #                        aws_access_key_id=access_key,
    #                        aws_secret_access_key=secret_key,
    #                        region_name='us-east-1')
    #
    #     try:
    #         sts.get_session_token()
    #     except botocore.exceptions.ClientError:
    #         logger.exception('Invalid AWs credentials')
    #         raise forms.ValidationError(
    #             'Unable to connect using the provided AWS credentials. Verify that "{}" and "{}" are correct.'.format(
    #                 self.fields['access_key'].label,
    #                 self.fields['secret_key'].label,
    #             )
    #         )
