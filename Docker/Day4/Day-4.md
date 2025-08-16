# Indice - Day-4
- [Indice - Day-4](#indice---day-4)
  - [1 - O que são Volumes e seus tipos](#1---o-que-são-volumes-e-seus-tipos)
      - [Referência](#referência)
  - [2 - Criando volume do tipo Bind](#2---criando-volume-do-tipo-bind)
      - [Referência](#referência-1)
  - [3 - Gerenciando volumes do tipo Volume](#3---gerenciando-volumes-do-tipo-volume)
      - [Referência](#referência-2)
  - [4 - Outras formas de montar volumes e storage drivers](#4---outras-formas-de-montar-volumes-e-storage-drivers)
    - [Storage drivers](#storage-drivers)
      - [Referência](#referência-3)
  - [5 - Criando volume do tipo tmpfs](#5---criando-volume-do-tipo-tmpfs)
      - [Referência](#referência-4)
  
## 1 - O que são Volumes e seus tipos

Volumes são diretórios externos ao container, que são montados diretamente nele, e dessa forma bypassam seu filesystem, ou seja, não seguem o padrão de camadas.
- Principal função é de persistir dados

Particularidades:
- O volume é inicializado quando o container é criado;
- Caso ocorra de já haver dados no diretório em que você está montando como volume, ou seja, se o diretório já existe e está "populado" na imagem base, aqueles dados serão copiados para o volume;
- Um volume pode ser reusado e compartilhado entre containers;
- Alterações em um volume são feitas diretamente no volume;
- Alterações em um volume não irão com a imagem quando você fizer uma cópia ou snapshot de um container;
    - Volumes continuam a existir mesmo se você deletar o container.

**Tipos**
- **Bind** - montar ele dentro do container, ideal para testes; pode montar um diretório ou arquivo
- **Volume** - cria um volume portável, monta informando o nome do volume
  - Por padrão, os volumes ficam no diretório `/var/lib/docker/volumes/` do host
- **tmpfs** - temporário, persiste na memória do host
  - Se o container para, os dados não são persistidos

#### Referência
- [Docker Docs: Storage](https://docs.docker.com/engine/storage/)

## 2 - Criando volume do tipo Bind

Com o bind, um arquivo ou diretório do host é montado para um container.

Qual flag escolher? `-v` ou `--mount`? 
- a flag `--mount` é mais explícita e detalhada
- a sintaxe `-v` combina todas as opções em um campo

```bash
## Flag --mount
docker run -ti --name testando-volumes --mount type=bind,src="/home/seu-user/giropops-senhas",target=/giropops-senhas debian

## Volume read-only - ro
docker run -ti --name testando-volumes --mount type=bind,src="/home/seu-user/giropops-senhas",target=/giropops-senhas,ro debian 
```

**Onde**
- `--mount` - indica o volume
- `type` - tipo de volume
- `src` - origem
- `dst` ou `target`- destino

#### Referência
- [Docker Docs: Bind mounts](https://docs.docker.com/storage/bind-mounts/)

## 3 - Gerenciando volumes do tipo Volume

É possível fazer a criação de volumes que serão consumidos por outros containers
- não é preciso criar uma pasta específica no host para persistir dados

Pode-se criar volumes isolados de containers.
- criar um volume portável, sem a necessidade de associá-lo a um container especial
Toda a sua administração através do comando: `docker volume create <nome_do_volume>`

No Linux, por padrão eles ficam em `/var/lib/docker/volumes` - mas cabe verificar com o comando `*inspect*`

```bash
## Listar os volumes criados
docker volume ls

## Criar um volume
docker volume create [nome_do_volume]

docker volume create giropops

## Inspecionar
docker volume inspect [nome_do_volume]

docker volume inspect [nome_do_volume]

## Montar o volume
docker run -ti --name testando-volumes3 --mount type=volume,src=giropops,target=/giropops debian

## Remover volume
docker volume rm [nome_do_volume]

## Remover volumes não usados
docker volume prune

```

#### Referência
-  [Docker Docs: Volumes](https://docs.docker.com/storage/volumes/)


## 4 - Outras formas de montar volumes e storage drivers

Usando a flag `-v`

```bash
docker container run -d --name container-teste -v volume-teste:/usr/share/nginx/html -p 8080:80 nginx### Exemplo

### Exemplo
docker run -d --name web-1 -v giropops:/usr/share/nginx/html -p 8080:80 nginx

## Readonly
docker container run -d --name container-teste -v volume-teste:/usr/share/nginx/html:ro -p 8080:80 nginx

### Exemplo
docker container run -d --name web-2 -v giropops:/usr/share/nginx/html:ro -p 8090:80 nginx

```

### Storage drivers

O Docker usa **Storage Drivers** para armazenar camadas de imagem e dados na camada gravável de um container.

Como os drivers podem ter desempenho inferior em gravações intensivas, especialmente em sistemas de copy-on-write, aplicações como bancos de dados sofrem impacto. 

Por isso, para dados persistentes, de alta escrita ou compartilhados entre containers, a prática recomendada é usar volumes Docker.

#### Referência
- [Docker Docs: Storage drivers](https://docs.docker.com/engine/storage/drivers/)

## 5 - Criando volume do tipo tmpfs

O tmpfs é um volume temporário que persiste apenas na memória do host.

```bash
## Usando a flag mount
docker container run -d --name container-teste --mount type=tmpfs,target=/app -p 8080:80 nginx

## Exemplo
docker run -d --name web-1 --mount type=tmpfs,target=/strigus -p 8080:80 nginx 

```

#### Referência
- [Docker Docs: tmpfs mounts](https://docs.docker.com/storage/tmpfs/)