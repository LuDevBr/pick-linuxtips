# Índice Day-2
- [Índice Day-2](#índice-day-2)
  - [1 - O que são imagens de container](#1---o-que-são-imagens-de-container)
  - [2 - Meu primeiro dockerfile](#2---meu-primeiro-dockerfile)
  - [3 - Conhecendo mais parâmetros do Dockerfile](#3---conhecendo-mais-parâmetros-do-dockerfile)
      - [Buildando](#buildando)
  - [4 - Dockerfile e o EntryPoint](#4---dockerfile-e-o-entrypoint)
      - [Buildando](#buildando-1)
  - [5 - Adicionando Healtcheck](#5---adicionando-healtcheck)
  - [6 - Utilizando o ADD](#6---utilizando-o-add)
  - [7 - Multistage](#7---multistage)
      - [Multistage - Dockerfile](#multistage---dockerfile)
  - [8 - ENV e ARG](#8---env-e-arg)
  - [9 - Pull, Push e Dockerhub](#9---pull-push-e-dockerhub)
      - [Fazendo push](#fazendo-push)
  - [Desafio prático 1](#desafio-prático-1)
  - [Desafio prático 2](#desafio-prático-2)


## 1 - O que são imagens de container

*“Uma imagem nada mais é que um container parado”*

A imagem é a abstração da infraestrutura em estado somente leitura, de onde será instanciado o container.
- Todo container é iniciado a partir de uma imagem, mas nunca há uma imagem em execução;
- Um container só pode ser iniciado a partir de uma única imagem.

Cada instrução no Dockerfile cria / adiciona mais uma camada.
- É no Dockerfile que vamos definir essas camadas;
  - Pensa em uma cebola e suas camadas 💡 rsrs

**Resumão**
- Uma imagem de contêiner é um pacote padronizado que inclui todos os arquivos, binários, bibliotecas e configurações para executar um container.

## 2 - Meu primeiro dockerfile

O Dockerfile é basicamente um arquivo de texto em que colocamos instruções para buildar uma imagem de container.
- Crie o arquivo chamado `Dockerfile`

```docker
### Imagem base
FROM ubuntu:18.04

## Executar comandos durante a criação da imagem
RUN apt-get update && apt-get install nginx -y

## Expor uma porta
EXPOSE 80

## Executar comandos quando o container for iniciado
CMD ["nginx", "-g", "daemon off;"]
```
Buildando a imagem e rodando o container:
```bash
## Buildar
docker image build -t meu-nginx:1.0 .

## Executar a imagem
docker run -d -p 8080:80 --name meu-nginx meu-nginx:1.0
```


## 3 - Conhecendo mais parâmetros do Dockerfile

```docker
## Imagem base
FROM ubuntu:22.04

## Executar comandos durante a criação da imagem
RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/list/*

## Expor uma porta
EXPOSE 80

## Copiar diretórios e arquivos do host
COPY index.html /var/www/html/

## Executar comandos quando o container for executado
CMD ["nginx", "-g", "daemon off;"]

## Alterar o diretório de trabalho - quando o container for iniciado
WORKDIR /var/www/html/

## Definir variáveis de ambiente
ENV APP_VERSION=1.0.0
```

**Onde**
-  `COPY` - é usado para copiar arquivos da estação onde está executando a construção para dentro da imagem
- `WORKDIR` - muda o diretório de trabalho - do "/" (raiz) para o especificado nele
- `ENV` - Define variáveis de ambiente

#### Buildando

```bash
## Buildar
docker image build -t meu-nginx:2.0 .

## Executar a imagem
docker run -d -p 8080:80 --name meu-nginx2 meu-nginx:2.0
```


## 4 - Dockerfile e o EntryPoint

```docker
## Imagem base
FROM ubuntu:22.04

## Label
LABEL maintainer="contato@lu.dev.br"

## Executar comandos durante a criação da imagem
RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/list/*

## Expor a porta 80
EXPOSE 80

## Copiar diretórios e arquivos do host
COPY index.html /var/www/html/

## Alterar o diretório de trabalho.
WORKDIR /var/www/html/

## Definir variáveis de ambiente
ENV APP_VERSION=1.0.0

## Principal processo do container
ENTRYPOINT ["nginx"]

## Parâmetros do processo executado pelo Entrypoint
CMD ["-g", "daemon off;"]
```

**Onde**
- `LABEL` - adiciona metadados à imagem, como versão, descrição e fabricante
- `ENTRYPOINT` - permite que você configure um container para rodar um executável. Quando esse executável for finalizado, o container também será.
  - É o principal processo do container

#### Buildando

```bash
## Buildar
docker image build -t meu-nginx:3.0 .

## Executar a imagem
docker run -d -p 8080:80 --name meu-nginx3 meu-nginx:3.0
```
## 5 - Adicionando Healtcheck
O `HELTHCHECK` verifica a integridade de um container na inicialização.
- aparece o status `health` na verificação.

```docker
## Imagem base
FROM ubuntu:22.04

## Label
LABEL maintainer="contato@lu.dev.br"

## Executar comandos durante a criação da imagem
RUN apt update && apt install -y nginx curl && rm -rf /var/lib/apt/list/*

## Expor a porta 80
EXPOSE 80

## Copiar diretórios e arquivos do host
COPY index.html /var/www/html/

## Alterar o diretório de trabalho
WORKDIR /var/www/html/

## Definir variáveis de ambiente
ENV APP_VERSION=1.0.0

## Principal processo do container
ENTRYPOINT ["nginx"]

## Parâmetros do processo executado pelo Entrypoint
CMD ["-g", "daemon off;"]

## Verificar a integridade de um container - curl localhost a cada 2s e finalizar se der erro
HEALTHCHECK --timeout=2s CMD curl localhost || exit 1
```

## 6 - Utilizando o ADD
O `ADD` copia novos arquivos, diretórios, arquivos TAR ou arquivos remotos e os adiciona ao filesystem do container.
- Se o arquivo estiver online, precisa de uma camada nova para descompactar.

```docker
## Imagem base
FROM ubuntu:22.04

## Label
LABEL maintainer="contato@lu.dev.br"

## Executar comandos durante a criação da imagem
RUN apt update && apt install -y nginx curl && rm -rf /var/lib/apt/list/*

## Expor a porta 80
EXPOSE 80

## Adicionar arquivos e diretórios locais ou remotos
ADD node_exporter-1.9.1.linux-amd64.tar.gz /root/node-exporter

## Copiar diretórios e arquivos do host
COPY index.html /var/www/html/

## Alterar o diretório de trabalho
WORKDIR /var/www/html/

## Definir variáveis de ambiente
ENV APP_VERSION=1.0.0

## Principal processo do container
ENTRYPOINT ["nginx"]

## Parâmetros do processo executado pelo Entrypoint
CMD ["-g", "daemon off;"]

## Verificar a integridade do container
HEALTHCHECK --timeout=2s CMD curl localhost || exit 1
```

## 7 - Multistage

Forma de fazer com que as imagens fiquem mais performáticas, menores
  - Usar o alpine é uma boa opção para fazer imagens menores

```docker
## Image base
FROM golang:1.18

## Workdir da aplicaão
WORKDIR /app

## Copiar tudo que está no mesmo nível do Dockerfile jogue para o dir do workdir /app
COPY hello.go ./

RUN go mod init hello

## Fazer o build
RUN go build -o /app/hello

## Execução do binário do go
CMD ["/app/hello"]
```

- Crie o arquivo `hello.go`:

```go
package main

import (
  "fmt"
)

func main(){
  fmt.Println("Hello Giropops!")
}
```

#### Multistage - Dockerfile

```docker
FROM golang:1.18 as buildando
WORKDIR /app
COPY . ./
RUN go mod init hello
RUN go build -o /app/hello

FROM alpine:3.15.9
COPY --from=buildando /app/hello /app/hello

CMD ["app/hello"]
```

**Onde**:
- No primeiro bloco:
  - `FROM golang AS buildando` - Estamos utilizando a imagem do Golang para criação da imagem de container, e estamos nomeando esse bloco como "buildando";
  - `ADD . ./` - Adicionando o código de nossa app dentro do container;
  - `WORKDIR /app` - Definindo que o diretório de trabalho é o "/app", ou seja, quando o *container* iniciar, estaremos nesse diretório;
  - `RUN go build -o /app/hello` - Vamos executar o *build* de nossa app Golang.
- No segundo bloco:
  - `FROM alpine:3.15.9` - Iniciando o segundo bloco e utilizando a imagem do Alpine para criação da imagem de container;
  - `COPY --from=buildando /app/hello /app/hello` - Aqui vamos copiar do bloco "buildando" um arquivo dentro de "/app/hello" para o diretório "/app" do container que estamos tratando nesse bloco, ou seja, copiamos o binário que foi compilado no bloco anterior e o trouxemos para esse;
  - `CMD ["/app/hello"]` - Aqui vamos executar a nossa app.

## 8 - ENV e ARG

- `ENV`: usado para criar variáveis de ambiente
- `ARG`: é valido somente no momento de build

```docker
FROM golang:1.18 as buildando
WORKDIR /app
COPY . ./
RUN go mod init hello
RUN go build -o /app/hello

FROM alpine:3.15.9
COPY --from=buildando /app/hello /app/hello
ENV APP="hello world" ## var de ambiente
ARG GIROPOPS="strigus" ## arg no momento de build
ENV GIROPOPS=$GIROPOPS
RUN echo "O giropops é: $GIROPOPS" ## run na arg
CMD ["app/hello"]

```

- Para alterar valor de um argumento na build da imagem é só adicionar a flag `--build-arg` mais o argumento:

```bash
## Exemplo
docker build -t go-teste:2.1 --build-arg GIROPOPS=catota .
```

## 9 - Pull, Push e Dockerhub

Registry: repositório que contém imagens de containers
- Pode ser público ou privado
  - EX: registry dentro da Cloud que uma empresa usa
**Docker Hub** é um repositório público e privado de imagens que disponibiliza diversos recursos como, por exemplo, sistema de autenticação, build automático de imagens, gerenciamento de usuários e departamentos de sua organização, entre outras funcionalidades.

Comandos utilizados:
- `Docker pull` - Baixa uma imagem do Docker Hub ou de outro registry
- `Docker push` - Envia uma imagem para o Docker Hub ou outro registry
- 'docker login` - Autentica o usuário
- `docker logout` - Desloga o usuário

```bash
## Baixar ou atualizar uma imagem de um registry
docker image pull [nome_da_imagem:tag]
docker image pull python:latest

## Remover a imagem
docker image rm id_da_imagem

## Docker login
docker login -u nome_de_usuario

#Docker logout
docker logout
```

#### Fazendo push

```bash
## Docker pull
docker pull nginx

## Listar imagens
docker image ls

## Renomear a imagem
docker image tag nginx:latest ludsilva/meu-nginx-teste:1.0

## Buildar a imagem
docker build -t ludsilva/meu-nginx-teste:1.0 .

## Fazer o pull
docker push

## Exemplo com app golang
docker image ls
docker tag go-teste:3.1 ludsilva/go-teste:4.0
docker build -t ludsilva/go-teste:4.0 .
docker push 

```

## Desafio prático 1
- Criar um Dockerfile com base Debian
  - não pode ser latest
- Ter healthcheck
- Rodar Nginx com entrypoint

## Desafio prático 2
- Resolver problemas contruindo Dockerfiles performáticos
    - Montar uma imagem de container a partir de uma app - contruir um Dockerfile e subir para o DockerHub