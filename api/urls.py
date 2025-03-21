from django.urls import path
from . import views

urlpatterns = [
    path("process", views.ProcessDataView.as_view())
]
