# Train and test during every image build, using the committed dataset.
# A changed dataset or Git commit invalidates the training layer.
FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py app.py generate_dataset.py config.json ./
COPY dataset/ ./dataset/
COPY tests/ ./tests/

ARG BUILD_COMMIT=local
ENV BUILD_COMMIT=${BUILD_COMMIT}
RUN python train.py && python -m unittest discover -s tests -v

# The service runs without root privileges.
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
