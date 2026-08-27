FROM python:3.12-slim

WORKDIR /app

COPY E-learing-fastapi/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY E-learing-fastapi .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
