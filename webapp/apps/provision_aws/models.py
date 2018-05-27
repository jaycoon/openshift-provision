import logging

from django.core.validators import RegexValidator
from django.db import models


logger = logging.getLogger(__name__)


class AWSRegion(models.Model):
    name = models.CharField(
        'Name',
        max_length=25,
        unique=True,
    )

    def __str__(self):
        return self.name


class AWSAccessKey(models.Model):
    name = models.CharField(
        'Name',
        max_length=100,
        unique=True,
    )
    access_key = models.CharField(
        'Access Key',
        max_length=100,
    )
    secret_key = models.CharField(
        'Secret Key',
        max_length=100,
    )

    def __str__(self):
        return '{name} [{access_key_masked}]'.format(
            name=self.name,
            access_key_masked=self.access_key[-4:].rjust(len(self.access_key), '*'),
        )


class AWSCluster(models.Model):
    # Cluster type choices
    CHOICE_CLUSTER_TYPE_MULTI = 'multi'
    CHOICE_CLUSTER_TYPE_AIO = 'aio'  # Not used yet
    CHOICE_CLUSTER_TYPE_HA = 'ha'  # Not used yet
    CLUSTER_TYPE_CHOICES = (
        (CHOICE_CLUSTER_TYPE_MULTI, '[multi] 1 master, 1 infra, 2 app'),
    )

    CHOICE_OPENSHIFT_VERSION_3_9 = '3.9'
    OPENSHIFT_VERSION_CHOICES = (
        (CHOICE_OPENSHIFT_VERSION_3_9, CHOICE_OPENSHIFT_VERSION_3_9),
    )

    CHOICE_EC2_AMI_TYPE_HOURLY = 'hourly'
    CHOICE_EC2_AMI_TYPE_CLOUD_ACCESS = 'cloud_access'
    EC2_AMI_TYPE_CHOICES = (
        (CHOICE_EC2_AMI_TYPE_HOURLY, 'Hourly'),
        (CHOICE_EC2_AMI_TYPE_CLOUD_ACCESS, 'Cloud Access'),
    )

    name = models.CharField(
        verbose_name='Cluster Name',
        max_length=63,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9\-]+$',
                message=('This field may contain only the ASCII letters "a" through "z", the digits "0" through "9",'
                         'and the minus sign ("-")')
            ),
        ],
        help_text='This value will be in your DNS entries and should conform to valid DNS characters.'
    )
    type = models.CharField(
        verbose_name='Cluster Type',
        max_length=10,
        choices=CLUSTER_TYPE_CHOICES,
        default=CHOICE_CLUSTER_TYPE_MULTI,
    )
    openshift_version = models.CharField(
        verbose_name='OpenShift Version',
        max_length=5,
        choices=OPENSHIFT_VERSION_CHOICES,
        default=CHOICE_OPENSHIFT_VERSION_3_9,
    )
    ec2_ami_type = models.CharField(
        verbose_name='EC2 AMI Type',
        max_length=20,
        choices=EC2_AMI_TYPE_CHOICES,
        default=CHOICE_EC2_AMI_TYPE_HOURLY,
        help_text=('If you have Cloud Access enabled, choose <strong>Cloud Access</strong>. Otherwise, '
                   'choose <strong>Hourly</strong>.')
    )
    ec2_key_name = models.CharField(
        verbose_name='EC2 Key Name',
        max_length=100,
    )
    ec2_private_key = models.TextField(
        verbose_name='EC2 Private Key',
        help_text='Enter the private key that matches the EC2 Key Pair selected above.'
    )
    route53_hosted_zone_id = models.CharField(
        verbose_name='Route53 Hosted Zone',
        max_length=30,
    )
    openshift_base_domain = models.CharField(
        verbose_name='OpenShift Base Domain',
        max_length=100,
        help_text=('The base domain for your cluster. The value should match or be a su`bdomain of the '
                   'Route53 Hosted Zone.'
                   '<br><br>'
                   'Example: If you set this to <code>example.com</code>, a DNS entry '
                   'of <code>&lt;cluster_name&gt;.example.com</code> will be created.')
    )
    rhsm_username = models.CharField(
        verbose_name='RHSM Username',
        max_length=100,
    )
    rhsm_password = models.CharField(
        verbose_name='RHSM Password',
        max_length=200,
    )
    rhsm_pool = models.CharField(
        verbose_name='RHSM Pool ID',
        max_length=100,
    )
    aws_access_key = models.ForeignKey(
        AWSAccessKey,
        verbose_name='AWS Access Key',
        on_delete=models.PROTECT,
    )
    aws_region = models.ForeignKey(
        AWSRegion,
        verbose_name='AWS Region',
        on_delete=models.PROTECT,
    )
