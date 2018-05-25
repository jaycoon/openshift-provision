import logging

import boto3
import botocore.exceptions
from django import forms
from django.db import models


logger = logging.getLogger(__name__)


class AWSAccessKey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    access_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)

    def __str__(self):
        return '{name} [{access_key_masked}]'.format(
            name=self.name,
            access_key_masked=self.access_key[-4:].rjust(4, '*'),
        )


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
