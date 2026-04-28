FROM python:3.11-slim

RUN adduser --disabled-password --gecos '' aceestuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly copy python files to avoid recursive directory copy warnings
COPY *.py ./

RUN chown -R aceestuser:aceestuser /app
USER aceestuser

EXPOSE 5000
CMD ["python", "app.py"]