from django.urls import path

from . import views


app_name = 'provision_aws'
urlpatterns = [
    path('', views.index, name='index'),

    path('keys/', views.AWSAccessKeyList.as_view(), name='key_list'),
    path('keys/add/', views.AWSAccessKeyCreate.as_view(), name='key_add'),
    path('keys/<int:pk>/update/', views.AWSAccessKeyUpdate.as_view(), name='key_update'),
    path('keys/<int:pk>/delete/', views.AWSAccessKeyDelete.as_view(), name='key_delete'),

    path('details/', views.details, name='details'),
]
