# Índice Day-3
- [Índice Day-3](#índice-day-3)
  - [1 - Conhecendo a App que precisamos transformar em container](#1---conhecendo-a-app-que-precisamos-transformar-em-container)
  - [2 - Transformando a nossa aplicação em uma imagem de container](#2---transformando-a-nossa-aplicação-em-uma-imagem-de-container)
    - [Dockerfile](#dockerfile)
    - [Build da imagem e execução dos containers](#build-da-imagem-e-execução-dos-containers)
  - [3 - Trabalhando com o tamanho e o número de camadas da imagem](#3---trabalhando-com-o-tamanho-e-o-número-de-camadas-da-imagem)
  - [4 - O que é Distroless e otimizando nossa imagem](#4---o-que-é-distroless-e-otimizando-nossa-imagem)
    - [Construindo o app com Chainguard](#construindo-o-app-com-chainguard)
    - [Referências](#referências)
  - [5 - Utilizando o Trivy para verificar vulnerabilidades](#5---utilizando-o-trivy-para-verificar-vulnerabilidades)
    - [Usando o Trivy](#usando-o-trivy)
  - [6 - Utilizando o Docker Scout](#6---utilizando-o-docker-scout)
  - [7 - Assinando nossa imagem e adicionando ao registry](#7---assinando-nossa-imagem-e-adicionando-ao-registry)
  - [Desafio prático 1](#desafio-prático-1)


## 1 - Conhecendo a App que precisamos transformar em container
Aplicação [Giropops Senhas](https://github.com/badtuxx/giropops-senhas.git)

```bash
## Clonar o repo do Github do App e acessar o diretorio
git clone https://github.com/badtuxx/giropops-senhas.git

cd giropops-senhas

## Instalar o pip
apt install pip -y

## Instalar as dependencias do python
pip install --no-cache-dir -r requirements.txt

## Faça a instalação do Redis e inicie o seu serviço
apt install redis
systemctl start redis

##Crie a variável de ambiente onde o valor seja o endereço IP ou hostname do host do Redis
export REDIS_HOST=localhost

##Execute o comando flask para iniciar o app - bindar um ip
flask run --host=0.0.0.0
```

## 2 - Transformando a nossa aplicação em uma imagem de container

### Dockerfile
```docker
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
COPY app.py .
COPY templates templates/
COPY static static/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

### Build da imagem e execução dos containers
```bash
docker image build -t giropops-senhas:1.0 .

## Executar container da aplicação
docker container run -d -e REDIS_HOST=<IP_DO_HOST> --name giropops-senhas -p 5000:5000 giropops-senhas:1.0

## Executar container do Redis
docker container run -d --name redis -p 6379:6379 redis
```

**OBS**: Certifique-se de substituir `<IP_DO_HOST>` pelo endereço IP ou hostname do host onde o Redis está rodando.

## 3 - Trabalhando com o tamanho e o número de camadas da imagem

Alterar a imagem base para a versão "slim" - reduz drasticamente o tamanho da imagem

```docker
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY app.py .
COPY templates templates/
COPY static static/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

## 4 - O que é Distroless e otimizando nossa imagem

Imagens "Distroless" contêm apenas os artefatos e dependências necessárias para a execução de um aplicativo
- não contêm gerenciadores de pacotes, shells ou quaisquer outros programas que você esperaria encontrar em uma distribuição Linux padrão;
  elimina a distribuição completa do sistema operacional
- sem imagem base, sem distribuição - uma camada - sem o `FROM`
Essas imagens contêm apenas o ambiente de runtime (como Node.js, Python, Java, etc.) e o aplicativo em si
Maior segurança
- Diminuir possibilidades de ter vulnerabilidades

Imagem menor com o alpine:
```docker
FROM python:3.11.12-alpine
WORKDIR /app
COPY requirements.txt .
COPY app.py .
COPY templates templates/
COPY static static/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["flask","run","--host=0.0.0.0"]
```

### Construindo o app com Chainguard


```docker
FROM cgr.dev/chainguard/python:latest-dev as buildando
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --user
COPY app.py .
COPY templates templates/
COPY static static/
ENTRYPOINT ["flask","run","--host=0.0.0.0"]
```

### Referências
- [Chainguard](https://images.chainguard.dev/)

## 5 - Utilizando o Trivy para verificar vulnerabilidades

O Trivy é um scanner de segurança abrangente e versátil. Ferramenta de código aberto, ele possui scanners que procuram problemas de segurança e aponta onde pode encontrar esses problemas:

- Pacotes de sistema operacional e dependências de software em uso (SBOM)
- Vulnerabilidades conhecidas (CVEs)
- Problemas e configurações incorretas de IaC
- Informações confidenciais e segredos
- Licenças de software

Para instalação, siga a documuentação oficial do Trivy: [Trivy Installation](https://trivy.dev/latest/getting-started/installation/).

### Usando o Trivy

```bash
trivy image <nome_da_imagem:tag>

## Exemplo
trivy image giropops-senhas:3.2
```

## 6 - Utilizando o Docker Scout

Solução do Docker para aprimorar proativamente a segurança da cadeia de suprimentos de software.

O Scout:
- Ajuda a identificar e corrigir vulnerabilidades em suas imagens de containers; ao analisar as imagens, o Docker Scout cria um inventário completo dos pacotes e camadas, também conhecido como Software Bill of Materials (SBOM);
- Este inventário é então correlacionado com um banco de dados de vulnerabilidades atualizado continuamente para identificar possíveis problemas de segurança
- É integrado ao Docker Desktop e ao Docker Hub;
- Também pode ser usado em uma pipeline de integração contínua, através da interface de linha de comando (CLI) do Docker e no Docker Scout Dashboard.

**Comandos**
- `compare`: para comparar duas imagens
- `cves`: para exibir as vulnerabilidades conhecidas
- `quickview`: para uma visão geral rápida de uma imagem
  `recommendations`: para exibir atualizações de imagens base disponíveis e recomendações de correção

**Instalação e uso básico do Docker Scout**:

```bash
## Instalação 
curl -fsSL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh -o install-scout.sh
sh install-scout.sh

## Uso
docker scout cves <nome_da_imagem:tag>

docker scout cves giropops-senhas:3.2

## Ver as recomendações
docker scout recommendations <nome_da_imagem:tag>
```

## 7 - Assinando nossa imagem e adicionando ao registry
Para assinar imagens de container podemos usar o Cosign, uma ferramenta que permite assinar e verificar imagens de container, garantindo a integridade e autenticidade das mesmas.

- [Sigstore](https://www.sigstore.dev/)
- [Cosign](https://github.com/sigstore/cosign)

```bash
## Instalando o Cosign 
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

## Gerar um par de chaves
cosign generate-key-pair

## Assinando imagens - a imagem tem que estar no DockerHub
cosign sign --key cosign.key nome_usuario_docker_hub/nome_da_images:tag

docker push ludsilva/giropops-senhas:3.0
cosign sign --key cosign.key ludsilva/giropops-senhas:3.0

## Verificar imagem assinada
cosign verify --key cosign.pub nome_usuario_docker_hub/nome_da_images:tag
cosign verify --key cosign.pub ludsilva/giropops-senhas:3.0
```

## Desafio prático 1
- Criar uma imagem Distroless / Chainguard, sem vulnerabilidades.
O desafio pode ser encontrado no repositório do Github: [Docker-multistage-distroless](https://github.com/ludsilva/docker-multistage-distroless)