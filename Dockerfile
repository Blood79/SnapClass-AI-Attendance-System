FROM python:3.11-slim
ARG BIOMETRIC=0
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-core.txt requirements-biometric.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-core.txt && if [ "$BIOMETRIC" = "1" ]; then apt-get update && apt-get install -y --no-install-recommends build-essential cmake && pip install --no-cache-dir -r requirements-biometric.txt && rm -rf /var/lib/apt/lists/*; fi
COPY . .
EXPOSE 8501
CMD ["streamlit","run","app/streamlit_app.py","--server.address=0.0.0.0","--server.port=8501"]
