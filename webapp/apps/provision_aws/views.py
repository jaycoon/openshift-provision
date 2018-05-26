from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import AWSAccessKey, AWSCluster
from .forms import AWSAccessKeyForm, AWSClusterForm


class AWSView(View):
    template_name = 'provision_aws/index.html'

    def get(self, request):
        aws_access_keys_count = AWSAccessKey.objects.count()

        return render(request, self.template_name, {
            'aws_access_keys_count': aws_access_keys_count,
        })


class AWSAccessKeyListView(ListView):
    model = AWSAccessKey
    context_object_name = 'aws_access_keys'


class AWSAccessKeyCreateView(CreateView):
    model = AWSAccessKey
    form_class = AWSAccessKeyForm
    context_object_name = 'aws_access_key'
    success_url = reverse_lazy('aws:key_list')


class AWSAccessKeyUpdateView(UpdateView):
    model = AWSAccessKey
    form_class = AWSAccessKeyForm
    context_object_name = 'aws_access_key'
    success_url = reverse_lazy('aws:key_list')


class AWSAccessKeyDeleteView(DeleteView):
    model = AWSAccessKey
    context_object_name = 'aws_access_key'
    success_url = reverse_lazy('aws:key_list')


class AWSClusterListView(ListView):
    model = AWSCluster
    context_object_name = 'aws_cluster'


class AWSClusterCreateView(CreateView):
    model = AWSCluster
    form_class = AWSClusterForm
    context_object_name = 'aws_cluster'
    success_url = reverse_lazy('aws:cluster_list')


class AWSClusterDeleteView(DeleteView):
    model = AWSCluster
    context_object_name = 'aws_cluster'
    success_url = reverse_lazy('aws:cluster_list')
