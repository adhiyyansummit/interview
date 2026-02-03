# Getting Started Guide

## Step 1: Install Dependencies

Activate the virtual environment and install requirements:

```bash
cd /Users/AKapoolia/Documents/interview
source interview_virtual_env/bin/activate
pip install -r requirements.txt
```

## Step 2: Setup Database

Run migrations to create tables:

```bash
python manage.py migrate
```

Create a superuser for the admin panel:

```bash
python manage.py createsuperuser
# Follow prompts to set username, email, password
```

## Step 3: Start the Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Step 4: Verify Setup

### Access the Admin Panel
Visit: http://localhost:8000/admin
- Login with your superuser credentials
- You should see: Customers, Loans, Task Executions, Users

### Test API Endpoints
```bash
# List loans (should be empty)
curl http://localhost:8000/api/loans/

# Response: []
```

## Step 5: Create Sample Data

### Option A: Using Django Shell
```bash
python manage.py shell

from django.contrib.auth.models import User
from loans.models import Customer, Loan, TaskExecution

# Create a user
user = User.objects.create_user(
    username='john_doe',
    email='john@example.com',
    password='testpass123'
)

# Create a customer
customer = Customer.objects.create(
    user=user,
    phone='9876543210'
)

# Create a loan
loan = Loan.objects.create(
    customer=customer,
    amount=500000.00,
    tenure_months=60,
    status='NEW'
)

# Create a task
task = TaskExecution.objects.create(
    loan=loan,
    task_type='KYC'
)

# Update loan with current task
loan.current_task = task
loan.status = 'IN_PROGRESS'
loan.save()

print(f"Created: {loan}")
print(f"Task: {task}")

exit()
```

### Option B: Using cURL (API)
```bash
# Create a loan (if no validation, this might work but is unsafe)
curl -X POST http://localhost:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer": 1,
    "amount": "100000.00",
    "tenure_months": 36,
    "status": "NEW"
  }'
```

## Step 6: Reproduce the Issues

### Issue 1: N+1 Queries
Enable query logging and check Django Debug Toolbar or logs:
```bash
# Check how many queries are executed
python manage.py shell

import django
django.setup()
from django.test.utils import CaptureQueriesContext
from django.db import connection
from loans.models import Loan

with CaptureQueriesContext(connection) as ctx:
    loans = list(Loan.objects.all())
    for loan in loans:
        _ = loan.customer.user.username  # Additional queries
    
print(f"Total queries: {len(ctx)}")
# Should show N+1 problem
```

### Issue 2: Race Condition
Open two terminal windows and run simultaneously:
```bash
# Terminal 1
curl -X POST http://localhost:8000/api/tasks/create/ \
  -H "Content-Type: application/json" \
  -d '{"loan_id": 1, "task_type": "KYC"}'

# Terminal 2 (run at the same time)
curl -X POST http://localhost:8000/api/tasks/create/ \
  -H "Content-Type: application/json" \
  -d '{"loan_id": 1, "task_type": "CREDIT_CHECK"}'

# Result: Both tasks created for same loan (BUG!)
```

Check in admin: Loan 1 will have 2 incomplete tasks

### Issue 3: No Permissions
```bash
# Anyone can access any loan
curl http://localhost:8000/api/loans/

# Try to create a loan without auth
curl -X POST http://localhost:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -d '{"customer": 1, "amount": "50000", "tenure_months": 12}'
```

## Step 7: Run Tests

```bash
python manage.py test loans
```

Expected output:
```
Creating test database for alias 'default'...
System check identified some issues:

WARNINGS:
...

Ran 3 tests in 0.123s

OK
```

## File Structure Verification

After setup, your structure should be:
```
interview/
├── manage.py
├── db.sqlite3 (created after migrate)
├── requirements.txt
├── README.md
├── TASKS.md
├── GETTING_STARTED.md (this file)
├── .gitignore
├── setup.sh
│
├── interview/
│   ├── __init__.py
│   ├── settings.py ✓ (updated with rest_framework & loans)
│   ├── urls.py ✓ (updated with include)
│   ├── asgi.py
│   └── wsgi.py
│
└── loans/
    ├── __init__.py
    ├── models.py ✓ (Customer, Loan, TaskExecution)
    ├── serializers.py ✓ (with vulnerabilities)
    ├── views.py ✓ (naive implementations)
    ├── urls.py ✓ (endpoint routing)
    ├── admin.py ✓ (admin configuration)
    ├── apps.py ✓
    ├── tests.py ✓
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'rest_framework'"
```bash
pip install -r requirements.txt
```

### "django.core.exceptions.ImproperlyConfigured"
Make sure `interview_virtual_env/bin/activate` is sourced

### "AttributeError: 'Loan' object has no attribute 'tasks'"
Run migrations:
```bash
python manage.py migrate
```

### Can't access http://localhost:8000/admin
- Make sure server is running
- Check the terminal for any error messages
- Try refreshing the page

## Next Steps

1. **Read** [README.md](README.md) - Full project overview
2. **Review** [TASKS.md](TASKS.md) - Quick task reference
3. **Start debugging** - See the 5 interview tasks
4. **Fix issues** - Make improvements and test

---

Need help? Check Django docs: https://docs.djangoproject.com/en/4.2/
