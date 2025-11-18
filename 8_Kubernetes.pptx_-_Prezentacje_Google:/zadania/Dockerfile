FROM python:3.11-slim


WORKDIR /app

RUN apt-get update && apt-get install -y \
   gcc \
   && rm -rf /var/lib/apt/lists/*

RUN pip install gradio

COPY . .

CMD ["python", "app.py"]