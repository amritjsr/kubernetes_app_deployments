FROM python:3.9-slim
WORKDIR /app
COPY src/ /app/
RUN pip install flask
CMD ["python", "app.py"]
EXPOSE 5000