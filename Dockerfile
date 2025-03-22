FROM python:3.10-slim

# Definições de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./lapscraping /lapscraping
COPY ./entrypoint.sh /entrypoint.sh

WORKDIR /lapscraping

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /lapscraping/requirements.txt && \
    adduser --disabled-password --no-create-home duser && \
    chown -R duser:duser /lapscraping && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]