FROM python:3.11-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
# RUN DJANGO_SUPERUSER_PASSWORD=a python manage.py createsuperuser --no-input --username=ric --email me@riccardo.top
COPY . .
EXPOSE 8000
# RUN python manage.py migrate
# RUN DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --no-input --username=admin --email me@riccardo.top
CMD ["python", "manage.py", "runserver", "0.0.0.0:8877"]