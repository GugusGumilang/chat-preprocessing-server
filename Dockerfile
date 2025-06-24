# =========================
# 1️⃣ BASE IMAGE
# =========================
FROM python:3.12-slim

# =========================
# 2️⃣ Install Dependencies
# =========================
RUN apt-get update && apt-get install -y git

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# 3️⃣ Copy Source
# =========================
COPY . /app
WORKDIR /app

# =========================
# 4️⃣ Expose port & Default Command
# =========================
EXPOSE 8080
CMD ["python", "main.py"]


