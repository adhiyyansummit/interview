from django.contrib import admin
from .models import Customer, Loan, TaskExecution


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')
    search_fields = ('user__username', 'phone')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount', 'status', 'current_task', 'created_at')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('customer__user__username', 'id')
    readonly_fields = ('created_at',)


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'task_type', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('task_type', 'is_completed', 'started_at')
    search_fields = ('loan__id', 'task_type')
    readonly_fields = ('started_at',)
