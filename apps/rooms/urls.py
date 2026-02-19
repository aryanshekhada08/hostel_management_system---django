from django.urls import include, path
from . import views

urlpatterns = [
    path('allocate/', views.allocate_room, name='allocate_room'),
    path('deallocate/<int:allocation_id>/', views.deallocate_room, name='deallocate_room'),
    path('ajax/allocate/', views.ajax_allocate_room, name='ajax_allocate_room'),
    path('ajax/deallocate/', views.ajax_deallocate_room, name='ajax_deallocate_room'),
    path('add-room/', views.add_room, name='add_room'),
    path('dashboard/', views.room_dashboard, name='room_dashboard'),
    path('my-room/', views.student_room_view, name='student_room'),
]
