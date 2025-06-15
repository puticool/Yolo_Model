# Base image với Python
FROM python:3.10-slim

# Cài ffmpeg (cho whisper, pydub hoạt động)
RUN apt-get update && apt-get install -y ffmpeg

# Tạo thư mục app
WORKDIR /app

# Copy toàn bộ project vào image
COPY . .

# Cài các package Python
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Cổng Railway yêu cầu bạn mở (Railway sẽ map port 10000 → public)
EXPOSE 10000

# Lệnh khởi chạy FastAPI (chỉnh nếu main app bạn ở file khác)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10000"]
