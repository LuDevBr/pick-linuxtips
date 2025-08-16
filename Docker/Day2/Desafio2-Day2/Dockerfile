FROM python:3.10 as buildando
LABEL maintainer="contato@lu.dev.br"
WORKDIR /app
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.10-alpine
WORKDIR /app
COPY --from=buildando /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=buildando /app /app
RUN apk add --no-cache curl
EXPOSE 3000
CMD ["python", "app.py"]
HEALTHCHECK --timeout=5s --interval=30s --retries=3 --start-period=20s CMD curl -f localhost:3000 || exit 1