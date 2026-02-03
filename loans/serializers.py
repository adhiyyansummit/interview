from rest_framework import serializers
from .models import Loan, TaskExecution, Customer


class TaskExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecution
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    tasks = TaskExecutionSerializer(many=True, read_only=True)

    class Meta:
        model = Loan
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
