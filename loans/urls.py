from django.urls import path
from .views import LoanListCreateView, TaskCreateView, TaskCompleteView

urlpatterns = [
    path("loans/", LoanListCreateView.as_view(), name="loan-list-create"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/complete/", TaskCompleteView.as_view(), name="task-complete"),
]
