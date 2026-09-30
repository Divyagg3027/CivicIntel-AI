FROM python:3.12-slim

WORKDIR /app

COPY . /app

CMD ["sh", "-c", "python -m http.server ${PORT} --bind 0.0.0.0"]