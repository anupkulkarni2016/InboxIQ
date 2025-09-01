# Dockerfile — streamlit dashboard image
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple

COPY . .

# Streamlit config
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
EXPOSE 8501

# mount history.csv via volume or bake it in
CMD ["python", "-m", "streamlit", "run", "app.py"]
