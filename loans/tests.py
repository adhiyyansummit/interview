from django.test import TestCase
from django.contrib.auth.models import User
from .models import Customer, Loan, TaskExecution


class LoanModelTests(TestCase):
    """Basic tests to verify models work"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='9999999999'
        )
    
    def test_loan_creation(self):
        loan = Loan.objects.create(
            customer=self.customer,
            amount=100000.00,
            tenure_months=12,
            status="NEW"
        )
        self.assertEqual(loan.status, "NEW")
        self.assertEqual(loan.customer, self.customer)
    
    def test_task_creation(self):
        loan = Loan.objects.create(
            customer=self.customer,
            amount=100000.00,
            tenure_months=12,
        )
        task = TaskExecution.objects.create(
            loan=loan,
            task_type="KYC"
        )
        self.assertEqual(task.is_completed, False)
        self.assertEqual(task.loan, loan)
