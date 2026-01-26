# -*- coding: utf-8 -*-
"""
Повне заповнення бази даними
python manage.py shell
exec(open('setup_all_data.py', encoding='utf-8').read())
"""

from datetime import date, timedelta
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

print("="*50)
print("Налаштування всіх даних HRM System")
print("="*50)

# 1. Стани заявок
print("\n1. Створення станів заявок...")
from requests.models import PendingState, ApprovedState, RejectedState

pending, created = PendingState.objects.get_or_create(pk=1)
print(f"   PendingState: {'створено' if created else 'існує'}")

approved, created = ApprovedState.objects.get_or_create(pk=1)
print(f"   ApprovedState: {'створено' if created else 'існує'}")

rejected, created = RejectedState.objects.get_or_create(pk=1)
print(f"   RejectedState: {'створено' if created else 'існує'}")

# 2. Стратегії зарплати
print("\n2. Створення стратегій зарплати...")
from employees.models import FixedSalaryStrategy, BonusSalaryStrategy

fixed_strategy, created = FixedSalaryStrategy.objects.get_or_create(
    pk=1,
    defaults={'monthly_amount': Decimal('25000.00')}
)
print(f"   FixedSalaryStrategy: {'створено' if created else 'існує'}")

fixed_strategy2, created = FixedSalaryStrategy.objects.get_or_create(
    pk=2,
    defaults={'monthly_amount': Decimal('45000.00')}
)
print(f"   FixedSalaryStrategy (45000): {'створено' if created else 'існує'}")

bonus_strategy, created = BonusSalaryStrategy.objects.get_or_create(
    pk=1,
    defaults={'base_salary': Decimal('30000.00'), 'bonus_percentage': Decimal('15.00')}
)
print(f"   BonusSalaryStrategy: {'створено' if created else 'існує'}")

# 3. Користувачі
print("\n3. Створення користувачів...")
from users.models import User, HR

user_maria, created = User.objects.get_or_create(
    username='maria',
    defaults={
        'email': 'maria@test.com',
        'role': 'employee',
        'first_name': 'Марія',
        'last_name': 'Іваненко'
    }
)
if created:
    user_maria.set_password('admin123')
    user_maria.save()
print(f"   User maria: {'створено' if created else 'існує'}")

user_olga, created = User.objects.get_or_create(
    username='olga_hr',
    defaults={
        'email': 'olga@test.com',
        'role': 'hr',
        'first_name': 'Ольга',
        'last_name': 'Петренко'
    }
)
if created:
    user_olga.set_password('admin123')
    user_olga.save()
print(f"   User olga_hr: {'створено' if created else 'існує'}")

user_ivan, created = User.objects.get_or_create(
    username='ivan',
    defaults={
        'email': 'ivan@test.com',
        'role': 'employee',
        'first_name': 'Іван',
        'last_name': 'Сидоренко'
    }
)
if created:
    user_ivan.set_password('admin123')
    user_ivan.save()
print(f"   User ivan: {'створено' if created else 'існує'}")

# 4. Співробітники
print("\n4. Створення співробітників...")
from employees.models import Employee

fixed_ct = ContentType.objects.get_for_model(FixedSalaryStrategy)
bonus_ct = ContentType.objects.get_for_model(BonusSalaryStrategy)

emp_maria, created = Employee.objects.get_or_create(
    email='maria@test.com',
    defaults={
        'first_name': 'Марія',
        'last_name': 'Іваненко',
        'phone': '+380501234567',
        'position': 'Розробник',
        'department': 'IT',
        'hire_date': date(2023, 1, 15),
        'salary_strategy_type': fixed_ct,
        'salary_strategy_id': fixed_strategy2.id
    }
)
if not created and not emp_maria.salary_strategy_type:
    emp_maria.salary_strategy_type = fixed_ct
    emp_maria.salary_strategy_id = fixed_strategy2.id
    emp_maria.save()
print(f"   Employee Марія: {'створено' if created else 'існує'}")

emp_olga, created = Employee.objects.get_or_create(
    email='olga@test.com',
    defaults={
        'first_name': 'Ольга',
        'last_name': 'Петренко',
        'phone': '+380502345678',
        'position': 'HR Менеджер',
        'department': 'HR',
        'hire_date': date(2022, 6, 1),
        'salary_strategy_type': bonus_ct,
        'salary_strategy_id': bonus_strategy.id
    }
)
print(f"   Employee Ольга: {'створено' if created else 'існує'}")

emp_ivan, created = Employee.objects.get_or_create(
    email='ivan@test.com',
    defaults={
        'first_name': 'Іван',
        'last_name': 'Сидоренко',
        'phone': '+380503456789',
        'position': 'Дизайнер',
        'department': 'Design',
        'hire_date': date(2023, 3, 20),
        'salary_strategy_type': fixed_ct,
        'salary_strategy_id': fixed_strategy.id
    }
)
# Виправити кракозябри якщо є
if emp_ivan.first_name != 'Іван':
    emp_ivan.first_name = 'Іван'
    emp_ivan.last_name = 'Сидоренко'
    emp_ivan.save()
print(f"   Employee Іван: {'створено' if created else 'існує'}")

# 5. HR менеджер
print("\n5. Створення HR менеджера...")
hr_olga, created = HR.objects.get_or_create(
    user=user_olga,
    defaults={
        'name': 'Ольга Петренко',
        'email': 'olga@test.com',
        'managed_departments': ['IT', 'Design', 'HR']
    }
)
print(f"   HR Ольга: {'створено' if created else 'існує'}")

# 6. Вакансії та кандидати
print("\n6. Створення вакансій та кандидатів...")
from documents.models import Vacancy, Candidate

vacancy1, created = Vacancy.objects.get_or_create(
    title='Python Developer',
    defaults={
        'department': 'IT',
        'description': 'Розробка веб-додатків на Django/Flask',
        'requirements': 'Python 3+, Django, PostgreSQL, Git',
        'salary_from': Decimal('40000.00'),
        'salary_to': Decimal('70000.00'),
        'is_active': True
    }
)
print(f"   Vacancy Python Developer: {'створено' if created else 'існує'}")

vacancy2, created = Vacancy.objects.get_or_create(
    title='UI/UX Designer',
    defaults={
        'department': 'Design',
        'description': 'Дизайн інтерфейсів для веб та мобільних додатків',
        'requirements': 'Figma, Adobe XD, досвід від 2 років',
        'salary_from': Decimal('35000.00'),
        'salary_to': Decimal('55000.00'),
        'is_active': True
    }
)
print(f"   Vacancy UI/UX Designer: {'створено' if created else 'існує'}")

vacancy3, created = Vacancy.objects.get_or_create(
    title='HR Manager',
    defaults={
        'department': 'HR',
        'description': 'Управління персоналом, рекрутинг',
        'requirements': 'Досвід в HR від 3 років',
        'salary_from': Decimal('30000.00'),
        'salary_to': Decimal('50000.00'),
        'is_active': False
    }
)
print(f"   Vacancy HR Manager (закрита): {'створено' if created else 'існує'}")

# Кандидати
cand1, created = Candidate.objects.get_or_create(
    email='petro@gmail.com',
    vacancy=vacancy1,
    defaults={
        'first_name': 'Петро',
        'last_name': 'Коваленко',
        'phone': '+380661234567',
        'resume': 'Python developer з 3 роками досвіду. Django, FastAPI, PostgreSQL.',
        'status': 'new'
    }
)
print(f"   Candidate Петро: {'створено' if created else 'існує'}")

cand2, created = Candidate.objects.get_or_create(
    email='anna@gmail.com',
    vacancy=vacancy1,
    defaults={
        'first_name': 'Анна',
        'last_name': 'Шевченко',
        'phone': '+380672345678',
        'resume': 'Junior Python developer, знаю Django basics.',
        'status': 'interview'
    }
)
print(f"   Candidate Анна: {'створено' if created else 'існує'}")

cand3, created = Candidate.objects.get_or_create(
    email='design@gmail.com',
    vacancy=vacancy2,
    defaults={
        'first_name': 'Олександр',
        'last_name': 'Бондар',
        'phone': '+380683456789',
        'resume': 'UI/UX designer, Figma, Sketch, 4 роки досвіду.',
        'status': 'offer'
    }
)
print(f"   Candidate Олександр: {'створено' if created else 'існує'}")

# 7. Заявки на відпустку (LeaveRequest)
print("\n7. Створення заявок на відпустку...")
from documents.models import LeaveRequest

lr1, created = LeaveRequest.objects.get_or_create(
    employee=emp_maria,
    start_date=date.today() + timedelta(days=30),
    defaults={
        'leave_type': 'vacation',
        'reason': 'Літня відпустка',
        'end_date': date.today() + timedelta(days=44),
        'status': 'approved'
    }
)
print(f"   LeaveRequest Марія (відпустка): {'створено' if created else 'існує'}")

lr2, created = LeaveRequest.objects.get_or_create(
    employee=emp_ivan,
    start_date=date.today() - timedelta(days=5),
    defaults={
        'leave_type': 'sick',
        'reason': 'Застуда',
        'end_date': date.today() - timedelta(days=2),
        'status': 'approved'
    }
)
print(f"   LeaveRequest Іван (лікарняний): {'створено' if created else 'існує'}")

# 8. Контракти
print("\n8. Створення контрактів...")
from documents.models import Contract

contract1, created = Contract.objects.get_or_create(
    employee=emp_maria,
    start_date=date(2023, 1, 15),
    defaults={
        'position': 'Розробник',
        'salary': Decimal('45000.00'),
        'status': 'approved'
    }
)
print(f"   Contract Марія: {'створено' if created else 'існує'}")

contract2, created = Contract.objects.get_or_create(
    employee=emp_olga,
    start_date=date(2022, 6, 1),
    defaults={
        'position': 'HR Менеджер',
        'salary': Decimal('34500.00'),
        'status': 'approved'
    }
)
print(f"   Contract Ольга: {'створено' if created else 'існує'}")

# 9. Записи робочого часу
print("\n9. Створення записів робочого часу...")
from timetracking.models import TimeRecord
from django.utils import timezone

for i in range(5):
    day = date.today() - timedelta(days=i)
    if day.weekday() < 5:  # Тільки робочі дні
        tr, created = TimeRecord.objects.get_or_create(
            employee=emp_maria,
            date=day,
            defaults={
                'clock_in_time': timezone.now().replace(hour=9, minute=0, second=0),
                'clock_out_time': timezone.now().replace(hour=18, minute=0, second=0)
            }
        )
        if created:
            print(f"   TimeRecord Марія {day}: створено")

print("\n" + "="*50)
print("ГОТОВО! Всі дані створено.")
print("="*50)
print("\nТестові акаунти:")
print("  Співробітник: maria / admin123")
print("  HR Менеджер:  olga_hr / admin123")
print("  Співробітник: ivan / admin123")
print("="*50)
