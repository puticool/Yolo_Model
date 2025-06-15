FROM python:3.11-slim

# Cài ffmpeg và các thư viện cần thiết
RUN apt-get update && \
    apt-get install -y gcc libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Đặt thư mục làm việc
WORKDIR /app

# Copy file requirements.txt và cài thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn
COPY . .

# Mở cổng 8000 (Railway sẽ tự ánh xạ)
EXPOSE 8000

# Chạy ứng dụng FastAPI (vì bạn để app trong main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
