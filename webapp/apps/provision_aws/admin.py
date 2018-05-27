from django.contrib import admin

from .models import AWSAccessKey, AWSCluster

admin.site.register(AWSAccessKey)
admin.site.register(AWSCluster)
