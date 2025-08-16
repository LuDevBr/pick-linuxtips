# Índice - Day 1
- [Índice - Day 1](#índice---day-1)
  - [1 - O que é um container?](#1---o-que-é-um-container)
    - [Namespaces e Cgroups](#namespaces-e-cgroups)
    - [Referências](#referências)
  - [2 - O que é Docker?](#2---o-que-é-docker)
  - [3 - Descomplicando Namespaces](#3---descomplicando-namespaces)
    - [Usando namespaces](#usando-namespaces)
      - [Debootstrap](#debootstrap)
      - [Unshare](#unshare)
      - [Montar o diretório /proc](#montar-o-diretório-proc)
      - [Listar namespaces](#listar-namespaces)
  - [4 - Descomplicando Cgrpoups](#4---descomplicando-cgrpoups)
    - [VM utilizada](#vm-utilizada)
    - [Adicionar o ambiente isolado ao Cgroup giropops](#adicionar-o-ambiente-isolado-ao-cgroup-giropops)
      - [Referências](#referências-1)
  - [5 - Copy-On-Write (COW) e como funciona](#5---copy-on-write-cow-e-como-funciona)
    - [Docker e sua relação com com Kernel Linux](#docker-e-sua-relação-com-com-kernel-linux)
  - [6 - Instalando o Docker Engine no Linux](#6---instalando-o-docker-engine-no-linux)
  - [7 - Criando e gerenciado os primeiros containers](#7---criando-e-gerenciado-os-primeiros-containers)
  - [8 - Visualizando métricas e a utilização de recursos pelos containers](#8---visualizando-métricas-e-a-utilização-de-recursos-pelos-containers)
  - [9 - Visualizando e inspecionando imagens e containers](#9---visualizando-e-inspecionando-imagens-e-containers)
  - [10 - Criando um container Dettached e o Docker exec](#10---criando-um-container-dettached-e-o-docker-exec)
  - [Desafio prático do Day 1](#desafio-prático-do-day-1)


## 1 - O que é um container?
Um Container pode ser definido como o agrupamento de uma aplicação junto com suas dependências, que compartilham o kernel do sistema operacional do host onde está rodando.

"*Containerizar*" é uma forma de isolar recursos para um determinado fim - de criar ambientes isolados.
- seja isolamento de CPU, RAM, usuários, processos, sistema de arquivos, etc.

Esse isolamento é possível graças ao **Cgroups** e **Namespaces**.

### Namespaces e Cgroups

**Cgroups** (Grupos de controle) são módulos do kernel do Linux que permitem limitar e isolar o uso de recursos como CPU, memória, I/O, rede, entre outros.

Já os **Namespaces** são funcionalidades do kernel do Linux que isolam ambientes, garantindo que cada container tenha sua própria visão de recursos como processos, sistema de arquivos, rede e usuários.

### Referências

- [What is a container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [What Are Namespaces and cgroups, and How Do They Work?](https://blog.nginx.org/blog/what-are-namespaces-cgroups-how-do-they-work)
- [Livro Descomplicando Docker](https://livro.descomplicandodocker.com.br/chapters/chapter_01.html)


## 2 - O que é Docker?

O Docker foi baseado no LXC, e iniciado em 2013, pela dotCloud (atual Docker Inc.)
   - Plataforma aberta para desenvolvimento e execução de aplicativos;
   - Permite separar aplicativos na infraestrutura - usando containers;
   - Enviar, testar e implantar código rapidamente.

Atualmente, o Docker é oficialmente suportado apenas em máquinas Linux 64 bits.


## 3 - Descomplicando Namespaces

Os *Namespaces* foram adicionados no kernel Linux na versão 2.6.24.
- Eles permitem o isolamento de processos quando estamos utilizando o Docker.

Alguns namespaces utilizados pelo Docker:
- **PID namespace**: permite que cada container tenha seus próprios IDs de processos;
- **Net** **namespace**: permite que cada container possua sua própria interface de rede e portas;
- **Mnt** **namespace**: permite que cada container seja ser dono de seu ponto de montagem, bem como de seu sistema de arquivos raiz;
- **IPC** **namespace**: provê um SystemV IPC isolado, além de uma fila de mensagens POSIX;
- **UST** **namespace**: provê o isolamento de *hostname*, nome de domínio, versão do SO, etc.;
- **User** **namespace**: responsável por manter o mapa de identificação de usuários em cada container.

### Usando namespaces

#### Debootstrap
O **debootstrap** é uma ferramenta que permite criar um sistema base a partir de um repositório Debian.
- Usado para criar um ambiente isolado, como um container ou uma máquina virtual.

```bash
## Instalar o debootstrap
apt-get update
apt-get install debootstrap -y

## Usar o debootstrap
debootstrap stable /debian http://deb.debian.org/debian

## Ver o sistema criado
cd /debian/
ls
```

**Onde:**
- `stable`: Versão do Debian
- `/debian`: Nome do dir de destino
- `http://deb.debian.org/debian`: Endereço do repositório do Debian

#### Unshare
O comando **unshare** permite executar um programa com determinados namespaces não compartilhados do processo pai, criando um ambiente isolado.

```bash
## Ushare 
unshare --mount --uts --ipc --net --map-root-user --user --pid --fork chroot /debian bash
```
#### Montar o diretório /proc

```bash
mount -t proc none /proc

## Verificando o isolamento - processos e rede
ps -ef
ip a

## Montar os diretorios /sys e /tmp
mount -t sysfs none /sys
mount -t tmpfs none /tmp
```

#### Listar namespaces

```bash
## Listar as namespaces
lsns
```

## 4 - Descomplicando Cgrpoups
**Cgroups** (grupos de controle) é um recurso do kernel Linux responsável por permitir a limitação da utilização de recursos do host pelos containers. 

Com o cgroups podemos gerenciar e limitar a utilização de CPU, memória, dispositivos, I/O, etc; bem como monitorar o uso dos recursos por processos e garantir o isolamento desses recursos.


### VM utilizada
Para este passo a passo foi utilizada uma Vagrant box (VM) ubuntu/bionic64 - você pode encontrar a box no [Vagrant Cloud](https://portal.cloud.hashicorp.com/vagrant/discover/ubuntu/bionic64).


```bash
## Instalar cgroups-tools
apt install cgroup-tools -y 

## *** OBS: no Ubuntu foi usado o comando ****
apt install cgroup-bin -y

## Criando um novo Cgroup - grupos de controle
cgcreate -g cpu,memory,blkio,devices,freezer:giropops

## Listando os diretórios associados ao cgroup CPU Giropops // se o grupo giropops tem controle sobre a CPU
ls /sys/fs/cgroup/cpu/giropops/

# Use o comando unshare para criar um ambiente isolado
unshare --mount --uts --ipc --net --map-root-user --user --pid --fork chroot /debian bash
```

- Para não encerrar o ambiente isolado, abra outro terminal no host. Use o comando ps -ef para listar os processos em execução e copie o PID do processo do bash - aqui no exemplo será o PID 2958.

### Adicionar o ambiente isolado ao Cgroup giropops

```bash
## Classificar os grupos

cgclassify -g cpu,memory,blkio,devices,freezer:giropops 2958

## Especificar a quota de uso de uso de CPU ao Cgroups giropops - usar 1% da CPU do host
cgset -r cpu.cfs_quota_us=1000 giropops
cat /sys/fs/cgroup/cpu/giropops/cpu.cfs_quota_us

## Limitar a memória
cat /sys/fs/cgroup/memory/giropops/
cgset -r memory.limit_in_bytes=48M giropops

## Ver o memory limit
cgget -r memory.limit_in_bytes giropops
```

#### Referências
- [Docs Kernel: Control Groups](https://docs.kernel.org/admin-guide/cgroup-v1/cgroups.html)
- [Docs RedHat: Introdução ao Grupos de Controle (Cgroups)](https://docs.redhat.com/pt-br/documentation/red_hat_enterprise_linux/6/html/resource_management_guide/ch01)

## 5 - Copy-On-Write (COW) e como funciona
> *It's a little bit like having a book. You can make notes in that book if you want, but each time you approach the pen to the page, suddenly someone shows up and takes the page and makes a xerox copy and hand it back to you, that's exactly how copy on write works. - Jérome Petezzoni*
> 
- O COW se refere que um novo recurso, seja ele um bloco no disco ou uma área em memória, só é alocado quando for modificado;
- o Docker usa um esquema de camadas (*layers)*, e para montar essas camadas são usadas técnicas de *Copy-On-Write*;
- Um container é basicamente uma pilha de camadas compostas por N camadas *read-only* e uma, a superior (a última camada), *read-write*;
    - Ou seja, a imagem de container nós não alteramos, ela é *read-only*;
- É imporante saber esse conceito para pensar estratégias de persistência de dados e manter as imagens mais limpas.


### Docker e sua relação com com Kernel Linux

O Docker utiliza algumas features básicas do kernel Linux para seu funcionamento.


## 6 - Instalando o Docker Engine no Linux
No querido Linux, segue instalação do Docker através do curl:

```bash
## Executar pelo bash o script
curl -fsSL https://get.docker.com | bash

## Para rodar os comandos sem o sudo (rootless)
dockerd-rootless-setuptool.sh install

## Saber a versão
docker version

## Listar containers em execução
docker container ls
docker ps

## Executar seu primeiro container - "Hello world"
docker container run hello-world

## Listar todos os containers
docker container ls -a
```

## 7 - Criando e gerenciado os primeiros containers

Executar um container com a imagem do Ubuntu e acessar o seu terminal - modo interativo:

```bash
docker container run -ti ubuntu
```

💡 Para sair do container cujo bash é o principal processo sem encerrá-lo, não use o comando `exit` ou `CTRL+D`, use `CTRL + P Q`

```bash
## Listar os containers
docker container ls -a

## Acessar um container em execução
docker container attach [ID ou nome do container]

## Exemplo
docker container run --name toskao -ti ubuntu

### dê o ctrl pq e depois:
docker container attach toskao
```

Iniciar, pausar e parar a execução de containers:

```bash
## Parar um container
docker container stop [ID ou nome do container]

## Iniciar um container
docker container start [ID ou nome do container]

## Restartar container
docker container restart [ID ou nome do container]

## Pausar um container
docker container pause [ID ou nome do container]

## Despausar um container
docker container unpause [ID ou nome do container]
```

Remover um container:
```bash
## Se ele não estiver parado, pare o container
docker container stop [ID ou nome do container]

## Remover um container
docker container rm [ID ou nome do container]

## Remover um container em execução (force)
docker container rm -f [ID ou nome do container]

## Remover todos containers parados - cuidado, hein!
docker container prune
```

## 8 - Visualizando métricas e a utilização de recursos pelos containers

```bash
## Mostrar estatísticas em execução (stats)
docker container stats [ID ou nome do container]

## Mostrar todos os containers
docker container stats -a

## Mostrar estatísticas - extrai apenas o primeiro resultado
docker container stats --no-stream

# Processos de um container em execução
docker container top [ID ou nome do container]

## Logs do container
docker container logs -f [ID ou nome do container]
```

## 9 - Visualizando e inspecionando imagens e containers

```bash
## Listar as imagens
docker image ls

## Remover uma imagem
docker rm image [image ID]

## Infos do container
docker container inspect [ID ou nome do container]

## Infos da imagem
docker image inspect [ID da imagem]
```

## 10 - Criando um container Dettached e o Docker exec

```bash
## Rodar container dettached - exemplo com Nginx
docker container run -d --name webserver nginx

## Docker exec
### Rodar comando em container em execução
docker container exec [ID ou nome do CONTAINER] <comando>
docker container exec  webserver ls -lha

### Bash em container executando
docker container exec -ti  [ID ou nome do CONTAINER] bash
docker container exec -ti webserver bash

## Fazer o pull de imagem
docker pull <nome da imagem:tag>
docker pull centos:7

## Criar um container sem executar
docker container create --name opa nginx
```

## Desafio prático do Day 1
Instalar o Docker no Linux.

- Utilizada uma [Vagrantbox Ubuntu 22.04](./Desafio-Day1/Vagrantfile) e um [shell script](./Desafio-Day1/script.sh) para automatizar a instalação do Docker e configuração do rootless mode.