import logging

from django.db import models


logger = logging.getLogger(__name__)


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
            access_key_masked=self.access_key[-4:].rjust(4, '*'),
        )


class AWSCluster(models.Model):
    # Cluster type choices
    CHOICE_CLUSTER_TYPE_MULTI = 'multi'
    CHOICE_CLUSTER_TYPE_AIO = 'aio'  # Not used yet
    CHOICE_CLUSTER_TYPE_HA = 'ha'  # Not used yet
    CLUSTER_TYPE_CHOICES = (
        (CHOICE_CLUSTER_TYPE_MULTI, '[multi] 1 master, 1 infra, 2 app'),
    )

    # AWS region choices
    CHOICE_AWS_REGION_AP_NORTHEAST_1 = 'ap-northeast-1'
    CHOICE_AWS_REGION_AP_NORTHEAST_2 = 'ap-northeast-2'
    CHOICE_AWS_REGION_AP_NORTHEAST_3 = 'ap-northeast-3'
    CHOICE_AWS_REGION_AP_SOUTH_1 = 'ap-south-1'
    CHOICE_AWS_REGION_AP_SOUTHEAST_1 = 'ap-southeast-1'
    CHOICE_AWS_REGION_AP_SOUTHEAST_2 = 'ap-southeast-2'
    CHOICE_AWS_REGION_CA_CENTRAL_1 = 'ca-central-1'
    CHOICE_AWS_REGION_CN_NORTH_1 = 'cn-north-1'
    CHOICE_AWS_REGION_EU_CENTRAL_1 = 'eu-central-1'
    CHOICE_AWS_REGION_EU_WEST_1 = 'eu-west-1'
    CHOICE_AWS_REGION_EU_WEST_2 = 'eu-west-2'
    CHOICE_AWS_REGION_EU_WEST_3 = 'eu-west-3'
    CHOICE_AWS_REGION_SA_EAST_1 = 'sa-east-1'
    CHOICE_AWS_REGION_US_EAST_1 = 'us-east-1'
    CHOICE_AWS_REGION_US_EAST_2 = 'us-east-2'
    CHOICE_AWS_REGION_US_WEST_1 = 'us-west-1'
    CHOICE_AWS_REGION_US_WEST_2 = 'us-west-2'
    AWS_REGION_CHOICES = (
        (CHOICE_AWS_REGION_AP_NORTHEAST_1, CHOICE_AWS_REGION_AP_NORTHEAST_1),
        (CHOICE_AWS_REGION_AP_NORTHEAST_2, CHOICE_AWS_REGION_AP_NORTHEAST_2),
        (CHOICE_AWS_REGION_AP_NORTHEAST_3, CHOICE_AWS_REGION_AP_NORTHEAST_3),
        (CHOICE_AWS_REGION_AP_SOUTH_1, CHOICE_AWS_REGION_AP_SOUTH_1),
        (CHOICE_AWS_REGION_AP_SOUTHEAST_1, CHOICE_AWS_REGION_AP_SOUTHEAST_1),
        (CHOICE_AWS_REGION_AP_SOUTHEAST_2, CHOICE_AWS_REGION_AP_SOUTHEAST_2),
        (CHOICE_AWS_REGION_CA_CENTRAL_1, CHOICE_AWS_REGION_CA_CENTRAL_1),
        (CHOICE_AWS_REGION_CN_NORTH_1, CHOICE_AWS_REGION_CN_NORTH_1),
        (CHOICE_AWS_REGION_EU_CENTRAL_1, CHOICE_AWS_REGION_EU_CENTRAL_1),
        (CHOICE_AWS_REGION_EU_WEST_1, CHOICE_AWS_REGION_EU_WEST_1),
        (CHOICE_AWS_REGION_EU_WEST_2, CHOICE_AWS_REGION_EU_WEST_2),
        (CHOICE_AWS_REGION_EU_WEST_3, CHOICE_AWS_REGION_EU_WEST_3),
        (CHOICE_AWS_REGION_SA_EAST_1, CHOICE_AWS_REGION_SA_EAST_1),
        (CHOICE_AWS_REGION_US_EAST_1, CHOICE_AWS_REGION_US_EAST_1),
        (CHOICE_AWS_REGION_US_EAST_2, CHOICE_AWS_REGION_US_EAST_2),
        (CHOICE_AWS_REGION_US_WEST_1, CHOICE_AWS_REGION_US_WEST_1),
        (CHOICE_AWS_REGION_US_WEST_2, CHOICE_AWS_REGION_US_WEST_2),
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
        'Cluster Name',
        max_length=30,
        unique=True,
        help_text='This value will be in your DNS entries and should conform to valid DNS characters.'
    )
    type = models.CharField(
        'Cluster Type',
        max_length=10,
        choices=CLUSTER_TYPE_CHOICES,
        default=CHOICE_CLUSTER_TYPE_MULTI,
    )
    aws_region = models.CharField(
        'AWS Region',
        max_length=25,
        choices=AWS_REGION_CHOICES,
        default=CHOICE_AWS_REGION_US_EAST_1,
    )
    openshift_version = models.CharField(
        'OpenShift Version',
        max_length=5,
        choices=OPENSHIFT_VERSION_CHOICES,
        default=CHOICE_OPENSHIFT_VERSION_3_9,
    )
    ec2_ami_type = models.CharField(
        'EC2 AMI Type',
        max_length=20,
        choices=EC2_AMI_TYPE_CHOICES,
        default=CHOICE_EC2_AMI_TYPE_HOURLY,
        help_text=('If you have Cloud Access enabled, choose <strong>Cloud Access</strong>. Otherwise, '
                   'choose <strong>Hourly</strong>.')
    )
    ec2_key_name = models.CharField(
        'EC2 Key Name',
        max_length=100,
    )
    ec2_private_key = models.TextField(
        'EC2 Private Key',
        help_text='Enter the private key that matches the EC2 Key Pair selected above.'
    )
    ec2_hosted_zone_id = models.CharField(
        'Route53 Hosted Zone',
        max_length=30,
    )
    openshift_base_domain = models.CharField(
        'OpenShift Base Domain',
        max_length=100,
        help_text=('The base domain for your cluster. The value should match or be a subdomain of the '
                   'Route53 Hosted Zone.'
                   '<br><br>'
                   'Example: If you set this to <code>example.com</code>, a DNS entry '
                   'of <code>&lt;cluster_name&gt;.example.com</code> will be created.')
    )
    rhsm_username = models.CharField(
        'RHSM Username',
        max_length=100,
    )
    rhsm_password = models.CharField(
        'RHSM Password',
        max_length=200,
    )
    rhsm_pool = models.CharField(
        'RHSM Pool ID',
        max_length=100,
    )
