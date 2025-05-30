FROM debian:12.11
LABEL mantainer="contato@lu.dev.br"
RUN apt update && apt install nginx curl -y && rm -rf /var/lib/apt/list/*
EXPOSE 80
COPY index.html /var/www/html/
WORKDIR /var/www/html/
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
HEALTHCHECK --interval=20s --timeout=5s --retries=5 CMD curl localhost || exit 1