import logging

import boto3
import botocore.exceptions
from django import forms

from .models import AWSAccessKey, AWSCluster, AWSRegion

logger = logging.getLogger(__name__)


class AWSTypedChoiceField(forms.TypedChoiceField):
    """
    Custom :py:class:`django.forms.TypedChoiceField` that accepts a max_length argument to support being a replacement
    field class in a :py:class:`django.forms.ModelForm` for a :py:class:`django.db.models.CharField`.
    """

    def __init__(self, max_length, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AWSAccessKeyForm(forms.ModelForm):
    class Meta:
        model = AWSAccessKey
        fields = '__all__'

    def clean(self):
        super().clean()

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


class AWSClusterPreForm(forms.Form):
    aws_access_key = forms.ModelChoiceField(
        label='AWS Access Key',
        required=True,
        queryset=AWSAccessKey.objects.order_by('name'),
        to_field_name='name',
        empty_label='',
    )
    aws_region = forms.ModelChoiceField(
        label='AWS Region',
        required=True,
        queryset=AWSRegion.objects.order_by('name'),
        to_field_name='name',
        empty_label='',
    )


class AWSClusterForm(forms.ModelForm):
    class Meta:
        model = AWSCluster
        fields = '__all__'
        exclude = [
            'aws_access_key',
            'aws_region',
            'provisioning',
        ]
        field_classes = {
            'ec2_key_name': AWSTypedChoiceField,
            'route53_hosted_zone_id': AWSTypedChoiceField,
        }
        widgets = {
            'rhsm_password': forms.PasswordInput,
        }

    def __init__(self, aws_access_key, aws_region, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.boto3_session = boto3.Session(
            aws_access_key_id=aws_access_key.access_key,
            aws_secret_access_key=aws_access_key.secret_key,
            region_name=aws_region.name,
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

        return choices
