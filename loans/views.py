from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Loan, TaskExecution
from .serializers import LoanSerializer


class LoanListCreateView(APIView):
    """
    List all loans (N+1 vulnerability) or create a new loan.

    """

    def get(self, request):
        loans = Loan.objects.all()  # N+1 + no filtering
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCreateView(APIView):
    """
    Create a task for a loan and set it as current_task.
    """

    def post(self, request):
        loan_id = request.data.get("loan_id")
        task_type = request.data.get("task_type")

        loan = Loan.objects.get(id=loan_id)

        task = TaskExecution.objects.create(
            loan=loan,
            task_type=task_type
        )

        loan.current_task = task
        loan.status = "IN_PROGRESS"
        loan.save()

        return Response({"message": "Task created"})


class TaskCompleteView(APIView):
    """
    Mark a task as completed.
    """

    def post(self, request):
        task_id = request.data.get("task_id")
        
        task = TaskExecution.objects.get(id=task_id)
        task.is_completed = True
        task.save()

        return Response({"message": "Task completed"})
