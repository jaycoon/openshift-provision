from django.urls import path

from . import views


app_name = 'provision_aws'
urlpatterns = [
    path('', views.AWSView.as_view(), name='index'),

    path('keys/', views.AWSAccessKeyListView.as_view(), name='key_list'),
    path('keys/add/', views.AWSAccessKeyCreateView.as_view(), name='key_add'),
    path('keys/<int:pk>/update/', views.AWSAccessKeyUpdateView.as_view(), name='key_update'),
    path('keys/<int:pk>/delete/', views.AWSAccessKeyDeleteView.as_view(), name='key_delete'),

    path('clusters/', views.AWSClusterListView.as_view(), name='cluster_list'),
    path('clusters/add/', views.AWSClusterCreateView.as_view(), name='cluster_add'),
    path('clusters/<int:pk>/delete/', views.AWSClusterDeleteView.as_view(), name='cluster_delete'),
]
