FROM python:3.11-slim

# Cài đặt các thư viện cần thiết cho OpenCV và các package khác
RUN apt-get update && \
    apt-get install -y gcc libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /src

# Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port
EXPOSE 8000

# Chạy ứng dụng FastAPI với Uvicorn
CMD ["uvicorn", "main:src", "--host", "0.0.0.0", "--port", "8000"]
