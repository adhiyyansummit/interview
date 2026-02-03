# Interview Task Cheat Sheet

## 🎯 5 Tasks at a Glance

### Task A: Performance (5-10 min)
**"The API is slow."**
- Location: `loans/views.py` - `LoanListCreateView.get()`
- Problem: N+1 queries
- Fix: Add `select_related()` and `prefetch_related()`

---

### Task B: Race Conditions (15-20 min)
**"Multiple tasks created for one loan."**
- Location: `loans/views.py` - `TaskCreateView.post()`
- Problem: No transaction, no locking, no validation
- Fix: Add `@transaction.atomic`, `select_for_update()`, validate active task

---

### Task C: Business Logic (10-15 min)
**"Enforce: Only one active task per loan."**
- Location: `loans/serializers.py` or service layer
- Problem: No validation layer
- Fix: Add validation in serializer `create()` method or service layer

---

### Task D: Data Consistency (10-15 min)
**"current_task points to completed task."**
- Location: `loans/models.py` and `loans/views.py`
- Problem: Manual pointer management, no atomic updates
- Fix: Clear `current_task` when task completes, update loan status

---

### Task E: Security (15-20 min)
**"Find 5+ security issues."**
- Location: Entire project
- Issues: No auth, no permissions, mass assignment, no validation, no rate limiting
- Fixes: Add authentication, object-level checks, field whitelisting, validators

---

## 📋 API Endpoints

```
GET/POST  /api/loans/           - List/create loans
POST      /api/tasks/create/    - Create task
POST      /api/tasks/complete/  - Complete task
```

## 🛠️ Quick Commands

```bash
# Migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run tests
python manage.py test loans

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## 📊 Model Relationships

```
User
  ↓
Customer
  ↓
Loan ← current_task (ForeignKey to TaskExecution)
  ↓
TaskExecution (many per loan)
```

## 💡 Key Concepts to Know

- Django ORM: `select_related()`, `prefetch_related()`, `values()`, `only()`
- Database: Transactions, locks, ACID properties
- Concurrency: Race conditions, pessimistic/optimistic locking
- REST: Authentication, permissions, validation
- Code: Separation of concerns, service layers

---

Good luck! 🚀
