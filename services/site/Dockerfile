FROM python:latest

COPY src site

CMD ["python", "-m", "http.server", "--directory", "/site", "80"]
