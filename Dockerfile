FROM node:22-alpine AS frontend
WORKDIR /app/frontapp
COPY frontapp/package*.json ./
RUN npm ci
COPY frontapp/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000
WORKDIR /app
COPY FlaskApp/requirements.txt ./FlaskApp/requirements.txt
RUN pip install --no-cache-dir -r FlaskApp/requirements.txt
COPY FlaskApp/ ./FlaskApp/
COPY --from=frontend /app/frontapp/build ./frontapp/build
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 10000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 60 FlaskApp.main:app"]
