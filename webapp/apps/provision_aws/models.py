from django.db import models


class AWSAccessKey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    access_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)

    def __str__(self):
        return '{name} [{access_key_masked}]'.format(
            name=self.name,
            access_key_masked=self.access_key[-4:].rjust(4, '*'),
        )
