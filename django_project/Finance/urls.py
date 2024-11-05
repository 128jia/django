from django.urls import path
from Finance import views

urlpatterns = [
     path('', views.fetch),
     path('form/', views.choose),
     path('get_stock_data/', views.get_stock_data1, name='get_stock_data1'),
     
     


]