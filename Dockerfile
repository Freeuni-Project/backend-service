# Dockerfile
FROM python:3.9
COPY requirements.txt /project-manager-app/requirements.txt
WORKDIR /project-manager-app
RUN pip install -r requirements.txt
COPY . /project-manager-app
ENTRYPOINT ["python"]
CMD ["run.py"]