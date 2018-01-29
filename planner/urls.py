from django.urls import path

from . import views

app_name = 'planner'
urlpatterns = [
    path('', views.index, name='index'),
    path('create_garden', views.create_garden, name='create_garden'),
    path('join_garden', views.join_garden, name='join_garden'),
    path('<int:gardenid>/add_bed', views.add_bed, name='add_bed'),
    path('<int:bedid>/delete_bed', views.delete_bed, name='delete_bed'),
    path('<int:garden_id>/', views.garden_view, name='garden_view'),
    path('<int:garden_id>/planification', views.planification_view, name='planification_view'),
    path('<int:garden_id>/planification/add_event', views.add_event, name='add_event')

]