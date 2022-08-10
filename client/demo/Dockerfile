# syntax=docker/dockerfile:1
FROM python:3.7-alpine
WORKDIR /aüü
#ENV FLASK_APP=app.py
#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
#EXPOSE 5000
COPY . .
CMD ["python", "demo.py"]