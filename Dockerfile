FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt upgrade && pip install --upgrade pip

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000/tcp

CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000"]