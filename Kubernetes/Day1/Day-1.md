# Índice - Day 1
- [Índice - Day 1](#índice---day-1)
  - [1 - O que é um container](#1---o-que-é-um-container)
  - [2 - Container Engine](#2---container-engine)
  - [3 - Container runtime](#3---container-runtime)
    - [Referências](#referências)
  - [4 - O que é a OCI](#4---o-que-é-a-oci)
  - [5 - O que é o Kubernetes](#5---o-que-é-o-kubernetes)
    - [Arquitetura do k8s](#arquitetura-do-k8s)
    - [Referências](#referências-1)
  - [6 - O que são workers e control plane do Kubernetes](#6---o-que-são-workers-e-control-plane-do-kubernetes)
  - [7 - Quais os componentes do control plane do Kubernetes](#7---quais-os-componentes-do-control-plane-do-kubernetes)
  - [8 - Quais os componentes dos workers do Kubernetes](#8---quais-os-componentes-dos-workers-do-kubernetes)
    - [Referências](#referências-2)
  - [9 - Quais as portas TCP e UDP dos componentes do Kubernetes](#9---quais-as-portas-tcp-e-udp-dos-componentes-do-kubernetes)
    - [**CONTROL PLANE ports**](#control-plane-ports)
    - [**WORKERS ports**](#workers-ports)
      - [Referência](#referência)
  - [10 - Introdução a pods, replica sets, deployments e service](#10---introdução-a-pods-replica-sets-deployments-e-service)
      - [Ferramentas](#ferramentas)
    - [Referências](#referências-3)
  - [11 - Entendendo e instalando o kubectl](#11---entendendo-e-instalando-o-kubectl)
      - [Documentação](#documentação)
  - [12 - Criando o nosso primeiro cluster com o kind](#12---criando-o-nosso-primeiro-cluster-com-o-kind)
    - [Criar cluster a partir de um arquivo](#criar-cluster-a-partir-de-um-arquivo)
      - [Documentação](#documentação-1)
  - [13 - Primeiros passos no k8s com o kubectl](#13---primeiros-passos-no-k8s-com-o-kubectl)
    - [Sintaxe](#sintaxe)
      - [Documentação](#documentação-2)
  - [14 - YAML e kubectl com dry-run](#14---yaml-e-kubectl-com-dry-run)
  - [Desafio prático](#desafio-prático)

## 1 - O que é um container

Um container é uma unidade leve e portátil que empacota uma aplicação com todas as suas dependências, garantindo que ela rode de forma consistente em qualquer ambiente.

Características:
- Isolamento de recursos - rede, recursos computacionais, processos, usuários, etc
- Diminui as camadas de complexidade que consomem recursos
- Uso dos namespaces e cgroups: módulos do kernel
    - isolamento de recursos (cpu e memória) - cgroup
    - isolamento de usuários, etc - namespaces

Containers são executados em cima de um *Container Engine* e de um *Container Runtime*

## 2 - Container Engine

O *Container Engine* é o responsável por gerenciar as imagens e volumes, ele é o encarregado de garantir que os os recursos utilizados pelos containers estão devidamente isolados, a vida do container, storage, rede, etc.
- responsável por fazer a criação do container, fazer health checks, pontos de volume, rede, etc
- não conversa diretamente com o kernel

Hoje temos diversas opções para se utilizar como *Container Engine*
- Opções como o Docker, o CRI-O e o Podman

O Docker é o Container Engine mais popular e ele utiliza como Container Runtime o *containerd*.

## 3 - Container runtime

Para que seja possível executar os containers nos nós é necessário ter um *Container Runtime* instalado em cada um desses nós.
- é o responsável por executar os containers nos nós.

Quando você está utilizando ferramentas como Docker ou Podman para executar containers em sua máquina, o seu Container Engine está fazendo uso de algum *Container Runtime* que:
- garante que o container está em execução
- conversa diretamente com o kernel para garantir o isolamento

Três tipos de *Container Runtime*:
- **Low level** - baixo nível - como runc, o crun e o runsc - são executados diretamente pelo Kernel
- **High level -** como containerd e CRI-O, são executados por um Container Engine
- **Sandbox e Virtualized** - são os *Container Runtime* que são executados por um *Container Engine* e que são responsáveis por executar containers de forma segura
    - o Sandbox é executado em unikernels ou utilizando algum proxy para fazer a comunicação com o Kernel (ex: gVisor)
    - o Virtualized é executado em máquinas virtuais (ex: Kata Containers)

### Referências
- [Livro Descomplicando Kubernetes - Day-1](https://github.com/badtuxx/DescomplicandoKubernetes/blob/main/pt/day-1/README.md#day-1)
- [Docker Docs: O que é um container?](https://www.docker.com/resources/what-container/)
- [Kubernetes Docs: Container Runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)

## 4 - O que é a OCI

**OCI** - [Open Container Iniciative](https://opencontainers.org/)
- Organização sem fins lucrativos que tem como objetivo padronizar a criação de containers  para que possam ser executados em qualquer ambiente

Fundada em 2015 pela Docker, CoreOS, Google, IBM, Microsoft, Red Hat e VMware e hoje faz parte da Linux Foundation

A OCI atualmente contém três especificações:
- Especificação de Tempo de Execução (runtime-spec);
- Especificação de Imagem (image-spec);
- Especificação de Distribuição (distribution-spec)

O *runc*, principal projeto desenvolvido pela OCI, é um container runtime de baixo nível amplamente utilizado por diversos Container Engines, incluindo o Docker.

## 5 - O que é o Kubernetes

Plataforma portátil, extensível e de código aberto para gerenciar cargas de trabalho e serviços em contêineres, que facilita tanto a configuração declarativa quanto a automação.

Desenvolvido pela Google, em meados de 2014, para atuar como um orquestrador de contêineres
- Inicialmente, era chamado de Borg em sua primeira versão; depois de Omega, que foi impulsionado pelo desejo de melhorar a engenharia de software do ecossistema Borg;
- Desenvolvido em Go.

Foi desenvolvido com um foco mais forte na experiência de desenvolvedores que escrevem aplicativos que são executados em um cluster. Seu principal objetivo é facilitar a implantação e o gerenciamento de sistemas distribuídos, enquanto se beneficia do melhor uso de recursos de memória e processamento que os contêineres possibilitam.

Facilita a tolerância a falhas, escalabilidade, uso de múltiplos serviços e proteção de dados sensitivos. Hoje é mantido pela CNCF - Cloud Native Computing Foundation.

### Arquitetura do k8s

![k8s-architecture](../../img/kubernetes-cluster-architecture.svg)

Segue um modelo *control plane/workers*, constituindo assim um cluster, onde para seu funcionamento é recomendado no mínimo três nós:

O nó ***control-plane***, responsável (por padrão) pelo gerenciamento do cluster
- garante a saúde, disponibilidade e capacidade do cluster
- armazena o estado do cluster
- o ideal é que cuide somente do gerenciamento

E os demais como ***workers***, responsáveis por executar as aplicações
- *é o cara que trabalha, né*

### Referências
- [Kubernetes Documentation - Overview](https://kubernetes.io/docs/concepts/overview/)

## 6 - O que são workers e control plane do Kubernetes

Um cluster Kubernetes consiste em um **Control Plane** e de **Workers -** chamados **Nodes** (nós).

O node Control Plane é responsável pelo gerenciamento do cluster
- garante a saúde, disponibilidade e capacidade do cluster;
- armazena o estado do cluster;
- o ideal é que cuide somente do gerenciamento, ou seja, que não execute aplicações.

Cada cluster precisa de pelo menos um node de **Worker** para executar **Pods**

## 7 - Quais os componentes do control plane do Kubernetes

Os componentes do **Control Plane** tem uma decisão global sobre o cluster (por exemplo, agendamento), assim como detectar e responder os eventos do cluster (por exemplo, inciar um novo Pod quando um campo de replicas de deploy não estiver satisfeito)
- podem ser executados em qualquer máquina do cluster

**Componentes do Control Plane**
- **API Server** - fornece uma API que utiliza JSON sobre HTTP para comunicação, onde para isto é utilizado principalmente o utilitário kubectl; expõe a API do Kubernetes
- comunicação por REST requests

- **etcd** - armazenamento do tipo chave-valor distribuído que o k8s utiliza para armazenar as especificações, status e configurações do cluster
  - todos os dados armazenados dentro do etcd são manipulados apenas através da API

- **Scheduler** - responsável por selecionar o nó que irá hospedar um determinado pod (a menor unidade de um cluster k8s)
  - as decisões de alocação são feitas baseando-se na quantidade de recursos disponíveis em cada nó, como também no estado de cada um dos nós do cluster

- **Controller Manager** - garante que o cluster esteja no último estado definido no etcd
  - executa os processos de **controlador**

- **cloud-controller-manager [](https://kubernetes.io/pt-br/docs/concepts/architecture/#cloud-controller-manager)** - componente da camada de gerenciamento do Kubernetes que incorpora a lógica de controle específica da nuvem

## 8 - Quais os componentes dos workers do Kubernetes

Os componentes do node executam em cada node, mantendo pods em execução e fornecendo o ambiente de runtime do Kubernetes.

**Componentes dos workers**
- **Kubelet** - é um agente do k8s que é executado nos nós workers.
  - em cada nó worker deverá existir um agente Kubelet em execução, encarregado de gerenciar efetivamente os pods direcionados pelo controller do cluster dentro dos nós
  - certifica que os containers estão sendo executados em um Pod
  - usa um conjunto de *PodSpecs* fornecidos por meio de vários mecanismos e garante que os containers descritos nesses *PodSpecs* estejam em execução e íntegros.

- **Kube-proxy** - um proxy de rede executado em cada nó no seu cluster, implementando parte do conceito de serviço do Kubernetes
  - age como um *proxy* e um *load balancer*
  - responsável por efetuar roteamento de requisições para os pods corretos, como também por cuidar da parte de rede do nó

- **Container runtime** - é o software responsável por executar os containers
  - O k8s suporta diversos agentes de execução de contêineres: Docker, containerd, CRI-O, e qualquer implementação do Kubernetes CRI (Container Runtime Interface)

### Referências
- [Kubernetes Documentation - Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)

## 9 - Quais as portas TCP e UDP dos componentes do Kubernetes

### **CONTROL PLANE ports**

| **Protocolo** | **Direção** | **Range** | **Propósito** | **Usada por** |
| --- | --- | --- | --- | --- |
| TCP | Inbound | 6443* | Kubernetes API server | All |
| TCP | Inbound | 2379-2380 | etcd server client API | kube-apiserver, etcd |
| TCP | Inbound | 10250 | Kubelet API | Self, **Control plane** |
| TCP | Inbound | 10259 /10251 | kube-scheduler | Self |
| TCP | Inbound | 10257 / 10252 | kube-controller-manager | Self |

- *Toda porta marcada por * é customizável, você precisa se certificar que a porta alterada também esteja aberta.*

### **WORKERS ports**

| **Protocolo** | **Direção** | **Range** | **Propósito** | **Usada por** |
| --- | --- | --- | --- | --- |
| TCP | Inbound | 10250 | Kubelet API | Self, Control plane |
| TCP | Inbound | 30000-32767 | NodePort | Services All |
| TCP | inbound | 10256 | kube-proxy | Self, Load balancers |


💡 *Todas as portas padrão podem ser substituídas. Quando portas personalizadas forem utilizadas, essas portas precisam ser abertas em vez dos padrões mencionados acima.*

#### Referência
- [Kubernetes Documentation - Kubernetes Ports and protocols](https://kubernetes.io/docs/reference/ports-and-protocols/)

## 10 - Introdução a pods, replica sets, deployments e service

- **Pod**: É o menor objeto do k8s, o k8s não trabalha com os contêineres diretamente, mas organiza-os dentro de ***pods***
  - são abstrações que dividem os mesmos recursos, como endereços, volumes, ciclos de CPU e memória, e uma especificação de como executar os containers
  - um pod pode possuir um ou vários containers

- **Deployment**: É um dos principais *controllers* utilizados.
  - em conjunto com o *ReplicaSet*, garante que determinado número de réplicas de um pod esteja em execução nos nós workers do cluster - fornece atualizações declarativas para Pods e ReplicaSets
  - também é responsável por gerenciar o ciclo de vida das aplicações, onde características associadas a aplicação, tais como imagem, porta, volumes e variáveis de ambiente, podem ser especificados em arquivos do tipo *yaml* ou *json* para posteriormente serem passados como parâmetro para o `kubectl` executar o deployment
  - cria o *ReplicaSet*

- **ReplicaSets**: É um objeto responsável por garantir a quantidade de pods em execução no nó;
  - é um controller
  - utilizado para garantir a disponibilidade de um número específico de Pods idênticos -  ou seja, tem que garantir quanto nós existem

- **Services**: método para expor um aplicativo de rede que está sendo executado como um ou mais Pods em seu cluster
  - forma de expor a comunicação através de um *ClusterIP*, *NodePort* ou *LoadBalancer* para distribuir as requisições entre os diversos Pods daquele Deployment.
  - Funciona como um balanceador de carga
  - É quem expõe o pod para fora do nó

#### Ferramentas
[Kind](https://kind.sigs.k8s.io/docs/user/quick-start) - ferramenta para execução de contêineres Docker que simulam o funcionamento de um cluster Kubernetes
- deve ser usado para fins didáticos, e não para produção

[Minikube](https://github.com/kubernetes/minikube) - ferramenta para implementar um *cluster* Kubernetes localmente com apenas um nó
- deve ser usado para fins didáticos, e não para produção

[MicroK8s](https://microk8s.io/) - pode ser utilizado em diversas distribuições e pode ser utilizado em ambientes de produção

[k3s](https://k3s.io/) - é um concorrente direto do MicroK8s, podendo ser executado inclusive em Raspberry Pi

[k0s](https://k0sproject.io/) - distribuição do Kubernetes com todos os recursos necessários para funcionar em um único binário, que proporciona uma simplicidade na instalação e manutenção do cluster
- pode ser usado para ambientes de produção


### Referências
- [Kubernetes Documentation - Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Kubernetes Documentation - Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Documentation - ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Kubernetes Documentation - Service](https://kubernetes.io/docs/concepts/services-networking/service/)

## 11 - Entendendo e instalando o kubectl

Ferramenta fundamental para trabalhar do cluster:
- Permite criar pods, services, etc;
- Interagir com a API do k8s;
- Feito em GO.

**Instalando o kubectl**

```bash
## Download - verificar na doc a versão
 curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
 
 ## Mudar a permissao do binário
 chmod +x kubectl
 
 ## Mover para bin
 mv kubectl /usr/local/bin

## Verificar a versão
kubectl version
```
#### Documentação
- [Kubernetes Doc - Install Tools](https://kubernetes.io/docs/tasks/tools/)

## 12 - Criando o nosso primeiro cluster com o kind

Usar o kind nos permite rodar um cluster Kubernetes localmente, o que é muito usado para estudos, testes e para ambiente de desenvolvimento.

```bash
## Instalar docker - pré requisito
curl -fsSL https://get.docker.com | bash

## Instalar kind - ver versão na documentação
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

## Criar primeiro cluster
kind create cluster

## Listar os clusters
kind get clusters

## Deletar o cluster
kind delete cluster
```

### Criar cluster a partir de um arquivo

Vamos criar um cluster multinode: um node Control Plane e dois Workers a partir do arquivo `.yaml`- nomeado como `kind-cluster.yaml`
- Procure se atentar com a apiVersion

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

O `kubectl` é o responsável por conversar com a API do k8s, então, quando criamos o cluster com o kind, ele já configura o `kubectl` para conversar com o cluster criado

```bash
## Simular um multi-node (do exemplo acima)
vim kind-cluster.yaml

## Comando para criar o cluster - a partir do arquivo .yam
kind create cluster --config kind-cluster.yaml --name giropops

## Listar os nodes
kubectl get nodes
```

#### Documentação
- [kind - Quick start](https://kind.sigs.k8s.io/docs/user/quick-start/)
 

## 13 - Primeiros passos no k8s com o kubectl

- O Kubernetes fornece uma ferramenta de linha de comando para comunicação com um cluster Kubernetes plano de controle, usando a API do Kubernetes: o `kubectl`

### Sintaxe

```bash
kubectl [command] [TYPE] [NAME] [flags]
```

Onde `command`, `TYPE`, `NAME`, e `flags`são:
- `command`: Especifica a operação que você deseja executar em um ou mais recursos, por exemplo `create`, `get`, `describe`, `delete`.
- `TYPE`: Especifica o tipo de recurso

Exemplos do comando

```bash
## Pegar detalhes
kubectl get [OPTIONS]

## Listar namespaces
kubectl get namespace

## Listar os pods da namespace
kubectl get pods -n kube-system

## Listar os pods com mais detalhes - IP e node - com o parâmetro -o wide
kubectl get pods -n kube-system -o wide

## Listar todos os pods do cluster - independente do namespace
kubectl get pods -A
kubectl get po

## Listar os deployments
kubectl get deployment

## Listar todos deployments
kubectl get deployment -A

#Listar services
kubectl get service
kubectl get svc

# Listar os ReplicaSets
kubectl get replicaset -A

## Listar ReplicaSets do namespace
kubectl get replicaset -n kube-system -o wide
```

Criando pods e brincando com o kubectl:

```bash
## Criar um pod - com container nginx
kubectl run --image nginx --port 80 giropops

## Acessar o pod - no caso, tem 1 container
kubectl exec -it giropops -- bash
>> root@giropops:/proc/1# cat cmdline
>> nginx: master process nginx -g daemon off;root@giropops:/proc/1# 

## Executar comandos
kubectl exec -it giropops -- ls /proc

## Delete pod
kubectl delete pods giropops

## Expondo e criar service nodeports - expor o serviço
kubectl expose pods giropops
kubectl expose pods giropops --type NodePort

## Services
kubectl get svc
kubectl delete service
```

#### Documentação
- [Command line tool (kubectl)](https://kubernetes.io/docs/reference/kubectl/)

## 14 - YAML e kubectl com dry-run

Uma outra forma de criar um pod ou qualquer outro objeto no Kubernetes é através da utilizaçâo de uma arquivo manifesto, que é uma arquivo em formato YAML onde você passa todas as definições do seu objeto.

```bash
## Dry-run - não criar um pod, apenas simula
kubectl run --image nginx --port 80 giropops --dry-run=client

## Mostra um YAML
kubectl run --image nginx --port 80 giropops --dry-run=client -o yaml

### Redirecionar - criar um template a partir de um pod
kubectl run --image nginx --port 80 giropops --dry-run=client -o yaml > pod.yaml

## Criar a partir do yaml
kubectl apply -f pod.yaml
```

- Exemplo do arquivo `YAML` gerado

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: "2025-05-09T12:16:58Z"
  labels:
    run: giropops
  name: giropops
  namespace: default
  resourceVersion: "4030"
  uid: 2b8b1029-e17e-4f88-b8a0-ea65f6cf6d91
spec:
  containers:
  - args:
    - dry-run=client
    image: nginx
    imagePullPolicy: Always
    name: giropops
    ports:
    - containerPort: 80
      protocol: TCP
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-2vpt6
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Always
  schedulerName: default-scheduler
  securityContext: {}
  serviceAccount: default
  serviceAccountName: default
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: kube-api-access-2vpt6
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607
          path: token
      - configMap:
          items:
          - key: ca.crt
            path: ca.crt
          name: kube-root-ca.crt
      - downwardAPI:
          items:
          - fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
            path: namespace
status:
  phase: Pending
  qosClass: BestEffort
                                                                                                                              44,1          48
```

## Desafio prático
- Criar um cluster kind com 1 nó control plane e 3 workers;
- Fazer deploy de um pod Nginx.

**1) Criando o cluster** - arquivo `kind-cluster.yaml`

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
    - role: control-plane
    - role: worker
    - role: worker
```

**2) Criar o cluster**
```bash
kind create cluster --config kind-cluster.yaml --name pick-nginx
```

**3) Criar um pod a partir de um manifesto YAML**
```bash
kubectl run --image nginx --port 80 giropops --dry-run=client -o yaml > pod.yaml

kubectl apply -f pod.yaml
```