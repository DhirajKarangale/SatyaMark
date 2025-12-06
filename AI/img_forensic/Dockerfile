FROM python:3.10-slim

# Install required system libs for mediapipe + cv2
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "img_forensic_worker.py"]
