# 1️⃣ PILIH BASE IMAGE
FROM python:3.12-slim

# 2️⃣ Set kerja directory
WORKDIR /app

# 3️⃣ Install git
RUN apt-get update && apt-get install -y git

# 4️⃣ Copy requirements
COPY requirements.txt .

# 5️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copy kode app
COPY . .

# 7️⃣ Expose port
EXPOSE 8000

# 8️⃣ Command untuk run app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
