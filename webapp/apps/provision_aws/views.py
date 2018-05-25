from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import AWSAccessKey, AWSAccessKeyForm
from .forms import AmazonWebServicesForm, AmazonWebServicesDetailsForm


class AWSAccessKeyList(ListView):
    model = AWSAccessKey
    context_object_name = 'aws_access_keys'


class AWSAccessKeyCreate(CreateView):
    model = AWSAccessKey
    form_class = AWSAccessKeyForm
    context_object_name = 'aws_access_key'
    success_url = reverse_lazy('aws:key_list')


class AWSAccessKeyUpdate(UpdateView):
    model = AWSAccessKey
    form_class = AWSAccessKeyForm
    context_object_name = 'aws_access_key'
    success_url = reverse_lazy('aws:key_list')


class AWSAccessKeyDelete(DeleteView):
    model = AWSAccessKey
    context_object_name = 'aws_access_key'
    success_url = reverse_lazy('aws:key_list')


def index(request):
    if request.method == 'POST':
        form = AmazonWebServicesForm(request.POST)
        if form.is_valid():
            request.session['aws_credentials'] = {
                'aws_access_key_id': form.cleaned_data['aws_access_key_id'],
                'aws_secret_access_key': form.cleaned_data['aws_secret_access_key'],
                'aws_region': form.cleaned_data['aws_region'],
            }

            return redirect('aws:details')
    else:
        form = AmazonWebServicesForm()

    return render(request, 'provision_aws/index.html', {
        'form': form,
    })


def details(request):
    aws_credentials = request.session.get('aws_credentials')
    if not aws_credentials:
        return redirect('aws:index')

    if request.method == 'POST':
        form = AmazonWebServicesDetailsForm(aws_credentials, request.POST)
        if form.is_valid():
            pass
    else:
        form = AmazonWebServicesDetailsForm(aws_credentials)

    return render(request, 'provision_aws/details.html', {
        'form': form,
    })
