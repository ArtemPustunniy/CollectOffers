FROM selenium/standalone-chrome:latest

USER root
RUN apt-get clean && apt-get update && \
    apt-get install -y python3 python3-pip python3-venv build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Создаем директорию /app, копируем код и папку ChromeProfile
RUN mkdir -p /app
WORKDIR /app
COPY . /app

# Устанавливаем переменную окружения, указывающую на ChromeProfile внутри /app
ENV CHROME_PROFILE="/app/ChromeProfile"

# Меняем владельца, чтобы seluser мог записывать в /app (включая ChromeProfile)
RUN chown -R seluser:seluser /app

USER seluser

RUN google-chrome --version
RUN chromedriver --version

RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

CMD ["/app/venv/bin/python", "sender.py"]
