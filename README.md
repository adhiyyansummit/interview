# Django + DRF Loan System Interview Assignment

A deliberately simplified but deep Django + Django REST Framework project designed to evaluate full-stack proficiency through real-world debugging and architectural challenges.

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
source interview_virtual_env/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user
python manage.py runserver
```

### 3. Access the Application
- **Admin Panel**: http://localhost:8000/admin
- **API Endpoints**:
  - `GET/POST /api/loans/` - List/Create loans
  - `POST /api/tasks/create/` - Create task for loan
  - `POST /api/tasks/complete/` - Mark task as completed

---

## 📋 Project Structure

```
interview/
├── manage.py
├── requirements.txt
├── db.sqlite3
│
├── interview/                    # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── loans/                        # Core app
    ├── models.py                # Customer, Loan, TaskExecution
    ├── serializers.py           # REST serializers
    ├── views.py                 # API views
    ├── urls.py                  # URL routing
    ├── admin.py                 # Admin interface
    ├── apps.py
    ├── tests.py
    └── migrations/
```

---

## 💾 Core Models

### Customer
- OneToOne relationship with Django User
- Phone field for contact

### Loan
- ForeignKey to Customer
- Amount & tenure
- Status: NEW → IN_PROGRESS → COMPLETED/REJECTED
- **workflow pointer**: `current_task` (ForeignKey to TaskExecution)
- Tracks active task in loan lifecycle

### TaskExecution
- ForeignKey to Loan
- Task types: KYC, CREDIT_CHECK, DISBURSEMENT
- Timestamps: `started_at`, `completed_at`
- Tracks workflow steps

---

## 🎯 Interview Tasks (Difficulty Escalation)

### TASK A: Performance Optimization
**Scenario**: "This API is slow. Fix it."

**Problem**: N+1 query problem in `LoanListCreateView.get()`
```python
loans = Loan.objects.all()  # Triggers query per loan for related objects
```

**Expected Fix**:
```python
loans = Loan.objects.select_related(
    'customer', 
    'customer__user', 
    'current_task'
).prefetch_related('tasks')
```

**Topics Covered**: ORM optimization, select_related, prefetch_related, query analysis

---

### TASK B: Race Condition & Concurrency
**Scenario**: "We're seeing multiple active tasks for one loan. Why?"

**Problems in `TaskCreateView.post()`**:
- No transaction wrapping
- No uniqueness constraint
- No database-level locking
- Multiple concurrent requests create multiple tasks

**Expected Fix**:
```python
from django.db import transaction

@transaction.atomic
def post(self, request):
    loan_id = request.data.get("loan_id")
    task_type = request.data.get("task_type")
    
    # Use select_for_update for pessimistic locking
    loan = Loan.objects.select_for_update().get(id=loan_id)
    
    # Validate no active task exists
    if loan.current_task and not loan.current_task.is_completed:
        return Response(
            {"error": "Loan already has an active task"},
            status=status.HTTP_409_CONFLICT
        )
    
    task = TaskExecution.objects.create(loan=loan, task_type=task_type)
    loan.current_task = task
    loan.status = "IN_PROGRESS"
    loan.save()
    
    return Response({"message": "Task created"}, status=status.HTTP_201_CREATED)
```

**Topics Covered**: Transactions, database locks, race conditions, concurrency, `select_for_update()`

---

### TASK C: Business Logic Validation
**Scenario**: "A loan can only have one active task at a time. Enforce it."

**Current Problem**:
- No validation layer
- Serializer accepts any data
- No business rule enforcement

**Expected Fix** (Serializer-level):
```python
class TaskExecutionSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        loan = validated_data['loan']
        
        # Check for active tasks
        active_task = TaskExecution.objects.filter(
            loan=loan,
            is_completed=False
        ).exists()
        
        if active_task:
            raise serializers.ValidationError(
                "Loan already has an active task."
            )
        
        return super().create(validated_data)
    
    class Meta:
        model = TaskExecution
        fields = "__all__"
```

**OR Service Layer Pattern**:
```python
class TaskService:
    @staticmethod
    def create_task(loan, task_type):
        if loan.current_task and not loan.current_task.is_completed:
            raise ValueError("Loan already has active task")
        return TaskExecution.objects.create(loan=loan, task_type=task_type)
```

**Topics Covered**: Validation layers, serializer hooks, service layer, business logic separation

---

### TASK D: Workflow Consistency
**Scenario**: "Sometimes `current_task` points to a completed task. Fix it."

**Problem**:
- `current_task` is manually set and never cleared
- No atomic status transitions
- Task can be marked complete without updating Loan

**Expected Fix**:
```python
class TaskExecutionSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        if validated_data.get('is_completed') and not instance.is_completed:
            # Mark as completed
            from django.utils import timezone
            instance.completed_at = timezone.now()
            instance.is_completed = True
            instance.save()
            
            # Update loan status
            loan = instance.loan
            if loan.current_task == instance:
                loan.current_task = None  # Clear pointer
                
                # Check if all tasks done
                pending = loan.tasks.filter(is_completed=False).exists()
                if not pending:
                    loan.status = "COMPLETED"
                else:
                    loan.status = "IN_PROGRESS"
                
                loan.save()
        
        return instance
    
    class Meta:
        model = TaskExecution
        fields = "__all__"
```

**Better**: State Machine Pattern
```python
class LoanStatusMachine:
    """Enforce valid state transitions"""
    TRANSITIONS = {
        "NEW": ["IN_PROGRESS"],
        "IN_PROGRESS": ["COMPLETED", "REJECTED"],
        "COMPLETED": [],
        "REJECTED": [],
    }
    
    @staticmethod
    def can_transition(from_status, to_status):
        return to_status in LoanStatusMachine.TRANSITIONS.get(from_status, [])
```

**Topics Covered**: State machines, atomic updates, consistency patterns, data integrity

---

### TASK E: Security Issues
**Scenario**: "What's unsafe in this codebase? Find 5+ issues."

**Security Issues**:

1. **Permissions Disabled**
   ```python
   REST_FRAMEWORK = {
       "DEFAULT_PERMISSION_CLASSES": [
           "rest_framework.permissions.AllowAny",  # ⚠️ ANYONE can access
       ]
   }
   ```
   **Fix**: Require authentication
   ```python
   "rest_framework.permissions.IsAuthenticated"
   ```

2. **No Object-Level Permissions**
   ```python
   loan = Loan.objects.get(id=loan_id)  # Any user can access any loan
   ```
   **Fix**: Verify ownership
   ```python
   loan = Loan.objects.get(id=loan_id, customer__user=request.user)
   ```

3. **Mass Assignment**
   ```python
   class LoanSerializer(serializers.ModelSerializer):
       class Meta:
           fields = "__all__"  # User can set ANY field
   ```
   **Fix**: Whitelist fields
   ```python
   fields = ['id', 'amount', 'tenure_months', 'customer']
   read_only_fields = ['status', 'current_task', 'created_at']
   ```

4. **No Input Validation**
   ```python
   amount = models.DecimalField(max_digits=10, decimal_places=2)  # No min/max
   tenure_months = models.IntegerField()  # No positive validation
   ```
   **Fix**: Add validators
   ```python
   from django.core.validators import MinValueValidator
   
   amount = models.DecimalField(
       max_digits=10,
       decimal_places=2,
       validators=[MinValueValidator(1000)]
   )
   tenure_months = models.IntegerField(
       validators=[MinValueValidator(1), MaxValueValidator(360)]
   )
   ```

5. **No Rate Limiting** - User can spam task creation

6. **SQL Injection Risk** - Minimal (Django ORM protects), but string queries possible

**Topics Covered**: Authentication, permissions, authorization, validation, mass assignment, rate limiting

---

## 💣 Built-in Traps & Discussion Points

| Trap | Why | Solution |
|------|-----|----------|
| **N+1 Queries** | Shows ORM understanding | `select_related`, `prefetch_related` |
| **Race Condition** | Concurrency testing | `transaction.atomic`, `select_for_update` |
| **Circular Reference** | Design patterns | Clear ownership, state machine |
| **No Validation** | Input safety | Serializers, validators, business logic |
| **No Permissions** | Security culture | Auth, RBAC, object-level checks |
| **Inconsistent State** | Data integrity | Atomic operations, constraints |
| **No Locking** | Database design | Optimistic/pessimistic locks |

---

## 🧪 Testing the Assignment

### Create Sample Data
```python
python manage.py shell

from django.contrib.auth.models import User
from loans.models import Customer, Loan

user = User.objects.create_user('john', 'john@test.com', 'pass123')
customer = Customer.objects.create(user=user, phone='9999999999')
loan = Loan.objects.create(
    customer=customer,
    amount=100000,
    tenure_months=12,
    status='NEW'
)
print(loan)
```

### Test API
```bash
# Create loan
curl -X POST http://localhost:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -d '{"customer": 1, "amount": "50000.00", "tenure_months": 24}'

# Create task (triggers race condition)
curl -X POST http://localhost:8000/api/tasks/create/ \
  -H "Content-Type: application/json" \
  -d '{"loan_id": 1, "task_type": "KYC"}'
```

---

## 📚 Learning Outcomes

After fixing these issues, candidate should understand:

- ✅ Django ORM query optimization
- ✅ Database transactions & ACID properties
- ✅ Concurrency & race conditions
- ✅ REST API security
- ✅ Validation & business logic layers
- ✅ State machine patterns
- ✅ Authentication & authorization
- ✅ Database locking strategies
- ✅ Code organization & separation of concerns
- ✅ Real-world debugging mindset

---

## 🔍 Conversation Flow (Interview Tips)

1. **Start Simple**: "Run this locally. Does it work?"
2. **Performance**: "Profiled? Too slow? Fix it."
3. **Concurrency**: "Two simultaneous requests create two tasks?"
4. **Architecture**: "Where should validation live?"
5. **Security**: "What breaks if I bypass the UI?"
6. **Tradeoffs**: "Why not optimistic locking? Pessimistic?"
7. **Real-World**: "How would you scale this to 1M loans?"

---

## 📝 Notes for Interviewer

- **Difficulty**: Mid to Senior level
- **Time**: 2-4 hours depending on depth
- **No gotchas**: All problems have real solutions
- **Extensible**: Add caching, async tasks, webhooks, etc.
- **Real patterns**: Everything mirrors production code

Happy interviewing! 🚀
