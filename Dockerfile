FROM python:3.12-slim
WORKDIR /code
RUN mkdir -p /code/logs && chmod 777 /code/logs
COPY ./app/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
