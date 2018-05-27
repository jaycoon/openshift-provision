from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from formtools.wizard.views import SessionWizardView

from .forms import AWSAccessKeyForm, AWSClusterForm, AWSClusterPreForm
from .models import AWSAccessKey, AWSCluster


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
    context_object_name = 'aws_clusters'


class AWSClusterDeleteView(DeleteView):
    model = AWSCluster
    context_object_name = 'aws_cluster'
    success_url = reverse_lazy('aws:cluster_list')


class AWSClusterWizardView(SessionWizardView):
    form_list = [
        AWSClusterPreForm,
        AWSClusterForm,
    ]
    template_name = 'provision_aws/awscluster_wizard.html'

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == '1':  # AWSClusterForm
            pre_form_data = self.get_cleaned_data_for_step('0')
            kwargs['aws_access_key'] = pre_form_data['aws_access_key']
            kwargs['aws_region'] = pre_form_data['aws_region']

        return kwargs

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)

        if step == '1':
            pre_form_data = self.get_cleaned_data_for_step('0')
            initial['aws_access_key'] = pre_form_data['aws_access_key']
            initial['aws_region'] = pre_form_data['aws_region']

        return initial

    def done(self, form_list, **kwargs):
        pre_form_data = self.get_cleaned_data_for_step('0')

        aws_cluster = kwargs['form_dict']['1'].save(commit=False)
        aws_cluster.aws_access_key = pre_form_data['aws_access_key']
        aws_cluster.aws_region = pre_form_data['aws_region']
        aws_cluster.save()

        return redirect(reverse_lazy('aws:cluster_list'))


class AWSClusterProvisionView(View):
    template_name = 'provision_aws/awscluster_provision.html'

    def get(self, request, pk):
        aws_cluster = AWSCluster.objects.get(pk=pk)

        

        return render(request, self.template_name, {
            'aws_cluster': aws_cluster,
        })
