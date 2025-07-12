from django.urls import path
from . import views

urlpatterns = [
    path('simulate/', views.simulate_heat),
    path('simulate/evolution/', views.simulate_heat_evolution_async),
    path('simulate/task-status/<str:task_id>/', views.get_task_status),
]
