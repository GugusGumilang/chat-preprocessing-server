# 1️⃣ Pilih base image python
FROM python:3.12-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy requirements.txt
COPY requirements.txt .

# 4️⃣ Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy seluruh kode
COPY . .

# 6️⃣ Expose port 8000
EXPOSE 8000

# 7️⃣ Command buat run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
