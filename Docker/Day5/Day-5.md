# Índice Day-5
- [Índice Day-5](#índice-day-5)
  - [1 - Descomplicando as Networks do Docker](#1---descomplicando-as-networks-do-docker)
    - [Referências](#referências)
  - [2 - Criando uma Network e conectando nossos containers](#2---criando-uma-network-e-conectando-nossos-containers)
  - [3 - Outras opções de rede para os nossos containers](#3---outras-opções-de-rede-para-os-nossos-containers)
  - [4 - Conectando containers em uma Network temporariamente](#4---conectando-containers-em-uma-network-temporariamente)
  - [5 - Limitando recursos como CPU e Memória](#5---limitando-recursos-como-cpu-e-memória)
    - [Referências](#referências-1)


## 1 - Descomplicando as Networks do Docker

As Networks do Docker são uma abstração criada para facilitar o gerenciamento da comunicação de dados entre containers e os nós externos ao ambiente docker.

- Drivers de rede:
  - Bridge: modo padrão
  - none: sem rede
  - host: remove o isolamento entre o container e o host
  - overlay: conecta vários hosts entre si, usado junto com Swarm
  - ipvlan: controle no endereçamento ipv4 e ipv6
  - macvlan: forma de ter containers como dispositivos de rede, atribuindo um MAC address

**Alguns comandos**
```bash
# Criar uma rede brigde
docker network create --driver bridge <nome_da_rede>

##Exemplo de criação de uma bridge network
docker network create --driver bridge isolated_nw

#Listar as redes
docker network ls

# Rodar um container na rede isolated_nw
docker container run -itd --net isolated_nw alpine sh

# Descobrir quais containers estão associados a uma rede
docker network inspect <nome_da_rede>
docker network inspect isolated_nw

## Conectar um container com uma bridge
docker network connect <nome_da_rede> [ID ou Container name]

## Desconectar o container em uma rede
docker network disconnect <nome_da_rede> [ID ou Container name]
```

### Referências
- [Docker Docs: Networking](https://docs.docker.com/reference/cli/docker/network/)
- [Docker Docs: Networking - Drivers](https://docs.docker.com/engine/network/drivers/)

## 2 - Criando uma Network e conectando nossos containers

Criar uma rede brigde e conectar dois containers

```bash
# Criar uma rede brigde
docker network create --driver bridge <nome_da_rede>
docker network create --driver bridge giropops-senhas

### Antes
docker container run -d -e REDIS_HOST=<IP_DO_HOST> --name giropops-senhas -p 5000:5000 giropops-senhas:1.0
docker container run -d --name redis -p 6379:6379 redis

### Agora
## Env com IP do Gateway da bridge criada - sabe quem é quem pelo nome do container (sem necessidade de IP)
docker run -d --name redis --network giropops-senhas -p 6379:6379 redis
docker run -d --name giropops-senhas --network giropops-senhas -e REDIS_HOST=redis -p 5000:5000 giropops-senha-test
```

## 3 - Outras opções de rede para os nossos containers

Exemplos:
- Executar um container com um DNS personalizado
- Usar o ``--link``

```bash
## Usando DNS Cloudflare
docker run -d --name giropops-senhas-2 --network giropops-senhas --dns 1.1.1.1 giropops-senha-test

## Link
docker container run -d --name redis -p 6379:6379 redis
docker container run -d --link redis:redis -e REDIS_HOST=redis --name giropops-senhas -p 5000:5000 giropops-senha-test
```

- Verificar as regras - iptables

```bash
sudo iptables -t nat -L
```

## 4 - Conectando containers em uma Network temporariamente

```bash
docker run -d --name redis --network giropops-senhas -p 6379:6379 redis

docker container run -d -e REDIS_HOST=redis --name giropops-senhas -p 5000:5000 giropops-senha-test

docker network connect giropops-senhas giropops-senhas 

## Conectar um container com uma bridge network
docker network connect <nome_da_rede> [ID ou Container name]

## Desconectar o container em uma rede
docker network disconnect <nome_da_rede> [ID ou Container name]
```

## 5 - Limitando recursos como CPU e Memória

```bash
## Limitar CPU
docker run -d --name redis --network giropops-senhas -p 6379:6379 --cpus 1 redis
docker inspect redis | grep -i cpus #### NanoCpus

## Limitar memoria
docker run -d --na
me redis --network giropops-senhas -p 6379:6379 --cpus 2 --memory 64m --memory-swap 128m redis

## CPU
docker container run --cpus 1 <nome_image:tag>

## Memoria e swap
docker container run --memory 64m --memory-swap 32m <nome_image:tag>
```

### Referências
- [Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)
