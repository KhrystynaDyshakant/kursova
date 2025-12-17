# kursova
# 1. Клонувати репозиторій

```
git clone git@github.com:KhrystynaDyshakant/kursova.git
cd Kursova
```

# 2. Створити віртуальне середовище

```
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

# 3. Встановити залежності

```
pip install django djangorestframework django-cors-headers
```

# 4. Застосувати міграції

```
python manage.py migrate
```

# 5. Створити суперюзера
```
python manage.py createsuperuser
```

# 6. Завантажити тестові дані

```
python manage.py loaddata fixtures/initial_data.json
```

# 7. Запустити сервер

```
python manage.py runserver
```

8. Відкрити в браузері

```
http://127.0.0.1:8000
```
