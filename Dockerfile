# Base image nhẹ chứa Python
FROM python:3.11-slim

# Cài ffmpeg và các thư viện hệ thống cần thiết cho whisper, pydub, OpenCV,...
RUN apt-get update && \
    apt-get install -y gcc libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Đặt thư mục làm việc mặc định
WORKDIR /app

# Copy file requirements.txt trước để cache install layer
COPY requirements.txt .

# Cài các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn
COPY . .

# Mở cổng ứng dụng (Railway sẽ map cổng này ra ngoài)
EXPOSE 8000

# Chạy FastAPI bằng uvicorn. Biến app được đặt tên là `src`
CMD ["uvicorn", "main:src", "--host", "0.0.0.0", "--port", "8000"]
