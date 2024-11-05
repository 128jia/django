from django.urls import path
from web_tool_w293 import views
from .views import show_data

urlpatterns = [
    path('', views.index),
    path('Browse/', views.Browse),
    path('search/', views.search),
    path('ajax/',views.find),
    path('show/', show_data, name='show_data'),
    path('ajax_data2/', views.crawl_data),
    

]