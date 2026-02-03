# Generated migration file
# This is auto-created by Django migrations system
# Run: python manage.py makemigrations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskExecution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(choices=[('KYC', 'KYC'), ('CREDIT_CHECK', 'Credit Check'), ('DISBURSEMENT', 'Disbursement')], max_length=30)),
                ('is_completed', models.BooleanField(default=False)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tenure_months', models.IntegerField()),
                ('status', models.CharField(choices=[('NEW', 'New'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('REJECTED', 'Rejected')], default='NEW', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('current_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_loans', to='loans.taskexecution')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loans.customer')),
            ],
        ),
        migrations.AddField(
            model_name='taskexecution',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='loans.loan'),
        ),
    ]
