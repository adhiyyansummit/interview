from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Loan(models.Model):
    STATUS_CHOICES = (
        ("NEW", "New"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("REJECTED", "Rejected"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure_months = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")

    # workflow pointer
    current_task = models.ForeignKey(
        "TaskExecution",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="active_loans",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan {self.id} - {self.customer}"


class TaskExecution(models.Model):
    TASK_TYPE_CHOICES = (
        ("KYC", "KYC"),
        ("CREDIT_CHECK", "Credit Check"),
        ("DISBURSEMENT", "Disbursement"),
    )

    loan = models.ForeignKey(
        Loan,
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_type} for Loan {self.loan_id}"
