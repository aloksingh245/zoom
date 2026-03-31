FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
  fastapi==0.110.* \
  uvicorn[standard]==0.27.* \
  httpx==0.27.* \
  pydantic==2.6.* \
  pydantic-settings==2.2.* \
  python-dateutil==2.9.* \
  tzdata==2024.*

COPY app ./app
COPY .env.example ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
