FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y gcc libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:src", "--host", "0.0.0.0", "--port", "8000"]
