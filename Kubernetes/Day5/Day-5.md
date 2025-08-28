# Índice - Day 5
- [Índice - Day 5](#índice---day-5)
  - [1 - O que é um cluster Kubernetes](#1---o-que-é-um-cluster-kubernetes)
      - [Documentação](#documentação)
  - [2 - Diferentes formas de instalar um cluster Kubernetes](#2---diferentes-formas-de-instalar-um-cluster-kubernetes)
  - [3 - Recomendações antes de começar](#3---recomendações-antes-de-começar)
      - [Documentação](#documentação-1)
    - [Criando as instâncias para o nosso cluster](#criando-as-instâncias-para-o-nosso-cluster)
  - [4 - Configurando os nossos nodes](#4---configurando-os-nossos-nodes)
  - [5 - Instalando e configurando o Containerd](#5---instalando-e-configurando-o-containerd)
    - [Configurando as portas](#configurando-as-portas)
  - [6 - Incializando o nosso cluster e o admin.conf](#6---incializando-o-nosso-cluster-e-o-adminconf)
    - [Entendendo o arquivo admin.conf](#entendendo-o-arquivo-adminconf)
    - [Seções do arquivo](#seções-do-arquivo)
    - [Diretórios dos certificados](#diretórios-dos-certificados)
      - [Documentação](#documentação-2)
  - [7 - Adicionando os outros nodes e o que é CNI](#7---adicionando-os-outros-nodes-e-o-que-é-cni)
    - [O que é o CNI?](#o-que-é-o-cni)
    - [Instalando o Weave Net](#instalando-o-weave-net)
      - [Documentação](#documentação-3)
  - [8 - Visualizando mais informações sobre os nodes](#8---visualizando-mais-informações-sobre-os-nodes)
    - [Desafio Day 5](#desafio-day-5)

## 1 - O que é um cluster Kubernetes

![kubernetes-architecture](../../img/kubernetes-cluster-architecture.svg)

Um cluster Kubernetes é um conjunto de nodes que trabalham juntos para executar todos os Pods.
- Diversos nós, diversas máquinas para fechar um cluster

Um cluster Kubernetes é composto por nodes que podem ser tanto **control plane** quanto **workers**. O control plane é responsável por gerenciar o cluster, enquanto os workers são responsáveis por executar os pods que são criados no cluster pelos usuários.

Em ambientes de produção, o *control plane* geralmente é executado em várias máquinas, e um cluster geralmente executa vários nodes, proporcionando tolerância a falhas e alta disponibilidade.

Componentes do ***control plane***:
- **etcd**: tem papel crucial na manutenção da estabilidade e confiabilidade do cluster;
  - armazena as informações de configuração de todos os componentes do control plane, incluindo os detalhes dos serviços, pods e outros recursos do cluster;
- **kube-apiserver**: é a principal interface de comunicação do Kubernetes, autenticando e autorizando solicitações, processando-as e fornecendo as respostas apropriadas;
- **kube-scheduler**: componente responsável por decidir em qual nó os pods serão executados, levando em consideração os requisitos e os recursos disponíveis;
- **kube-controller-manager**: é responsável por gerenciar os diferentes controladores que regulam o estado do cluster e mantêm tudo funcionando.

Componentes dos ***workers***:
- **kubelet**: é o agente que funciona em cada nó do cluster, garantindo que os containers estejam funcionando conforme o esperado dentro dos pods;
- **kube-proxy:** é o componente responsável fazer ser possível que os pods e os services se comuniquem entre si e com o mundo externo;
- **Container runtime:** componente fundamental que capacita o Kubernetes a executar contêineres com eficiência;
- E todos os Pods das aplicações.

#### Documentação
- [Kubernetes Doc - Architecture](https://kubernetes.io/docs/concepts/architecture/)

## 2 - Diferentes formas de instalar um cluster Kubernetes

Usaremos o `kubeadm`, mas existem outras formas de instalar o Kubernetes
- **kubeadm**: Ferramenta que automatiza a criação e configuração de clusters Kubernetes, incluindo control plane e nodes. Altamente configurável para clusters personalizados.
- **Kubespray**: Usa Ansible para implantar clusters Kubernetes. Permite personalização da rede, réplicas do control plane, tipo de armazenamento, entre outros. Ideal para nuvens públicas e privadas.
- **Cloud Providers**: Provedores como AWS, GCP e Azure oferecem modelos prontos para criar clusters Kubernetes facilmente. Muitos também oferecem serviços gerenciados.
- **Kubernetes Gerenciados**: Serviços como EKS (AWS), GKE (Google) e AKS (Azure) cuidam da configuração e manutenção do cluster. O usuário gerencia apenas os aplicativos.
- **Kops**: Ferramenta para criar e gerenciar clusters Kubernetes em nuvens públicas. Oferece personalização e escalabilidade, mas pode ser mais complexa para iniciantes.
- **Minikube e kind**: Criam clusters locais de nó único. Ótimos para testes, aprendizado e desenvolvimento de aplicações sem necessidade de ambiente em produção.

## 3 - Recomendações antes de começar

Principais pré-requisitos:
  - Linux
  - 2 GB ou mais de RAM por máquina (menos de 2 GB não é recomendado)
  - 2 CPUs ou mais
  - Conexão de rede entre todas os nodes no cluster (pode ser via rede pública ou privada)

Algumas portas precisam estar abertas para que o cluster funcione corretamente, as principais:
- Porta **6443**: É a porta padrão usada pelo *Kubernetes API Server* para se comunicar com os componentes do cluster. É a porta principal usada para gerenciar o cluster e deve estar sempre aberta.
- Portas **10250-10255**: Essas portas são *usadas pelo kubelet para se comunicar com o control plane* do Kubernetes. A porta **10250** é usada para comunicação de leitura/gravação e a porta **10255** é usada apenas para comunicação de leitura.
  - Libere até 10259
- Porta **30000-32767**: Essas portas são usadas para serviços *NodePort* que precisam ser acessíveis fora do cluster. O Kubernetes aloca uma porta aleatória dentro desse intervalo para cada serviço NodePort e redireciona o tráfego para o pod correspondente.
- Porta **2379-2380**: Essas portas são usadas pelo *etcd*, o banco de dados de chave-valor distribuído usado pelo control plane do Kubernetes. A porta 2379 é usada para comunicação de leitura/gravação e a porta 2380 é usada apenas para comunicação de eleição.

#### Documentação
- [Kubernetes Doc - Install kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)
   

### Criando as instâncias para o nosso cluster

Criar 3 instâncias Ubuntu - t2.medium na AWS:
- Acesso via SSH e key-pair
- Abrir as regras no SG para as portas:
  - **6443 -** para o SG das instâncias, sem necessidade de liberar para toda a internet
  - range **10250-10259 -** para o SG das instâncias
  - range **30000-32767 -** para o SG das instâncias
  - range **2379-2380 -** para o SG das instâncias

## 4 - Configurando os nossos nodes

Os passos para configurar os nodes - devem ser executados em todas as máquinas
- Desativar a swap - pois o Kubernetes não trabalha bem com swap ativado
- Carregar os módulos do kernel necessários para o funcionamento do Kubernetes
- Configurar alguns parâmetros do sistema. Isso garantirá que nosso cluster funcione corretamente
- Instalar os pacotes do Kubernetes

```bash
# Desativar a swap
sudo swapoff -a

# Carregando os módulos do kernel
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# Configurando parâmetros do sistema
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system

# Instalando os pacotes do Kubernetes - kubelet, kubeadm e kubectl
sudo apt-get update && sudo apt-get install -y apt-transport-https curl

sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

```

## 5 - Instalando e configurando o Containerd

Comandos para instalar e configurar o Containerd:

```bash
## Instalar

sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update && sudo apt-get install -y containerd.io

## Configurar
sudo containerd config default | sudo tee /etc/containerd/config.toml

sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

sudo systemctl restart containerd
sudo systemctl status containerd

## Habilitar o serviço do kubelet 
sudo systemctl enable --now kubelet
```

### Configurando as portas

Precisamos ter as portas TCP 6443, 10250-10255, 30000-32767 e 2379-2380 abertas entre os nodes do cluster.
- Por agora o que precisamos garantir são as portas TCP 6443 somente no `control plane` e as 10250-10255 abertas em todos nodes do cluster.
- Em nosso exemplo vamos utilizar como CNI o Weave Net, que é um CNI que utiliza o protocolo de roteamento de pacotes do Kubernetes para criar uma rede entre os pods.
  - precisamos abrir a porta TCP 6783 e as portas UDP 6783 e 6784, para que o Weave Net funcione corretamente.

Em resumo: não se esqueça de abrir as portas TCP 6443, 10250-10255 e 6783 no seu firewall.

## 6 - Incializando o nosso cluster e o admin.conf

Para configurar o endereço IP que o API Server anunciára para Nodes Control Plane criados com `init` e `join`, a flag `--apiserver-advertise-address` pode ser usada
- Substitua pelo endereço IP da máquina que está atuando como `control plane`

```bash
## Iniciar o node Control plane
sudo kubeadm init --pod-network-cidr=10.10.0.0/16 --apiserver-advertise-address=<IP_Control_plane>

sudo kubeadm init --pod-network-cidr=10.10.0.0/16 --apiserver-advertise-address=192.168.56.51

# Para começar a usar seu cluster, você precisa executar o seguinte como um usuário comum:
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Alternativamente, se você for o usuário root, você pode executar
export KUBECONFIG=/etc/kubernetes/admin.conf
```

### Entendendo o arquivo admin.conf

É o arquivo de configuração do `kubectl` (cliente de linha de comando) para se comunicar com um cluster Kubernetes.
- `vim $HOME/.kube/config`

Contém informações de acesso ao cluster, como endereço do servidor API, certificados e tokens de autenticação. Pode armazenar configurações para vários clusters (ex: desenvolvimento e produção), permitindo alternar facilmente entre eles.

⚠️ É um arquivo sensível. Quem tiver acesso a ele pode obter controle total do cluster. É gerado automaticamente durante a inicialização do cluster Kubernetes.

Exemplo de um arquivo `admin.conf` - do livro ![Descomplicando o Kubernetes](https://github.com/badtuxx/DescomplicandoKubernetes/tree/main):

```yaml
apiVersion: v1

clusters:
- cluster:
    certificate-authority-data: SEU_CERTIFICADO_AQUI
    server: https://172.31.57.89:6443
  name: kubernetes

contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes

current-context: kubernetes-admin@kubernetes

kind: Config

preferences: {}

users:
- name: kubernetes-admin
  user:
    client-certificate-data: SUA_CHAVE_PUBLICA_AQUI
    client-key-data: SUA_CHAVE_PRIVADA_AQUI
```

Simplificando, temos a seguinte estrutura:

```yaml
apiVersion: v1
clusters:
#...
contexts:
#...
current-context: kind-kind-multinodes
kind: Config
preferences: {}
users:
#...
```

### Seções do arquivo

**Clusters**

A seção clusters contém informações sobre os clusters Kubernetes que você deseja acessar, como o endereço do servidor API e o certificado de autoridade. Neste arquivo, há somente um cluster chamado kubernetes, que é o cluster que acabamos de criar.

```yaml
- cluster:
    certificate-authority-data: SEU_CERTIFICADO_AQUI
    server: https://172.31.57.89:6443
  name: kubernetes
```

**Contextos**

A seção contexts define configurações específicas para cada combinação de cluster, usuário e namespace. Nós somente temos um contexto configurado. Ele é chamado kubernetes-admin@kubernetes e combina o cluster kubernetes com o usuário kubernetes-admin.

```yaml
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
```

**Contexto atual**

A propriedade `current-context` indica o contexto atualmente ativo, ou seja, qual combinação de cluster, usuário e namespace será usada ao executar comandos kubectl. Neste arquivo, o contexto atual é o kubernetes-admin@kubernetes.

```yaml
current-context: kubernetes-admin@kubernetes
```

**Preferências**

A seção `preferences` contém configurações globais que afetam o comportamento do kubectl. Aqui podemos definir o editor de texto padrão, por exemplo.

```yaml
preferences: {}
```

**Usuários**

A seção users contém informações sobre os usuários e suas credenciais para acessar os clusters. Neste arquivo, há somente um usuário chamado kubernetes-admin. Ele contém os dados do certificado de cliente e da chave do cliente.

```yaml
- name: kubernetes-admin
  user:
    client-certificate-data: SUA_CHAVE_PUBLICA_AQUI
    client-key-data: SUA_CHAVE_PRIVADA_AQUI
```

- **Token de autenticação**: É um token de acesso que é usado para autenticar o usuário que está executando o comando kubectl. Esse token é gerado automaticamente quando o cluster é inicializado. Esse token é usado para autenticar o usuário que está executando o comando kubectl. Esse token é gerado automaticamente quando o cluster é inicializado.
- **certificate-authority-data**: Este campo contém a representação em base64 do certificado da autoridade de certificação (CA) do cluster. A CA é responsável por assinar e emitir certificados para o cluster. O certificado da CA é usado para verificar a autenticidade dos certificados apresentados pelo servidor de API e pelos clientes, garantindo que a comunicação entre eles seja segura e confiável.
- **client-certificate-data**: Este campo contém a representação em base64 do certificado do cliente. O certificado do cliente é usado para autenticar o usuário ao se comunicar com o servidor de API do Kubernetes. O certificado é assinado pela autoridade de certificação (CA) do cluster e inclui informações sobre o usuário e sua chave pública.
- **client-key-data**: Este campo contém a representação em base64 da chave privada do cliente. A chave privada é usada para assinar as solicitações enviadas ao servidor de API do Kubernetes, permitindo que o servidor verifique a autenticidade da solicitação. A chave privada deve ser mantida em sigilo e não compartilhada com outras pessoas ou sistemas.

### Diretórios dos certificados

```bash
sudo ls /etc/kubernetes/pki/
```
- **client-certificate-data**: O arquivo de certificado do cliente geralmente é encontrado em /etc/kubernetes/pki/apiserver-kubelet-client.crt.
- **client-key-data**: O arquivo da chave privada do cliente geralmente é encontrado em /etc/kubernetes/pki/apiserver-kubelet-client.key.
- **certificate-authority-data**: O arquivo do certificado da autoridade de certificação (CA) geralmente é encontrado em /etc/kubernetes/pki/ca.crt.

Caso você queira, você pode acessar o conteúdo do arquivo `admin.conf` com o seguinte comando:

```bash
kubectl config view
```

#### Documentação
- [Kubernetes Doc - Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
- [Livro: Descomplicando o Kubernetes - Day 5](https://github.com/badtuxx/DescomplicandoKubernetes/blob/main/pt/day-5/README.md#day-5)

## 7 - Adicionando os outros nodes e o que é CNI

Usar o `kubeadm` para fazer o join, porém ao invés de executar o comando no node do control plane, nesse momento precisamos rodar o comando diretamente no node que queremos adicionar ao cluster

```bash
kubeadm join 172.20.0.10:6443 --token abcd123.bhiyqbaqldu47894 --discovery-token-ca-cert-hash sha256:aaa359d6da9bd5f8f0155d33b3c000a78386ee052b17f044c6dcc37be02ffzzz

sudo kubeadm init --pod-network-cidr=10.10.0.0/16 --apiserver-advertise-address=192.168.56.51
```

**Comandos**
O comando `kubeadm join` inicializa um novo Node Kubernetes e o une ao cluster existente.
- **kubeadm join**: O comando base para adicionar um novo nó ao cluster.
- **172.31.57.89:6443**: Endereço IP e porta do servidor de API do nó mestre (control plane). Neste exemplo, o nó mestre está localizado no IP 172.31.57.89 e a porta é 6443.
- **-token if9hn9.xhxo6s89byj9rsmd**: O token é usado para autenticar o nó trabalhador no nó mestre durante o processo de adesão. Os tokens são gerados pelo nó mestre e têm uma validade limitada (por padrão, 24 horas). Neste exemplo, o token é if9hn9.xhxo6s89byj9rsmd.
- **-discovery-token-ca-cert-hash sha256:ad583497a4171d1fc7d21e2ca2ea7b32bdc8450a1a4ca4cfa2022748a99fa477**: Este é um hash criptográfico do certificado da autoridade de certificação (CA) do control plane. Ele é usado para garantir que o nó worker esteja se comunicando com o nó do control plane correto e autêntico. O valor após sha256: é o hash do certificado CA.

Os tokens têm validade de 24h. Caso o token já tenha expirado ou você não tenha copiado a saída do comando kubeadm init, utilize o comando abaixo para gerar um novo token e exibir o kubeadm join, que deverá ser executado para adicionar um novo node ao cluster:

```bash
kubeadm token create --print-join-command
```

### O que é o CNI?

**CNI (Container Network Interface)** é uma especificação e conjunto de bibliotecas usadas para configurar interfaces de rede em containers.
- Permite integrar diferentes soluções de rede ao Kubernetes, facilitando a comunicação entre Pods e serviços.
- Diversos plugins seguem a especificação CNI, como o **Weave Net**, que é um dos plugins de rede utilizados no Kubernetes.

Entre os plugins de rede mais utilizados no Kubernetes, temos:

- **Calico**: Plugin de rede popular que utiliza BGP para rotear tráfego entre os nós. Oferece desempenho escalável e suporte a políticas de rede e segurança.
- **Flannel**: Plugin simples e fácil de configurar. Cria uma rede overlay que permite a comunicação entre Pods em diferentes nós, utilizando um intervalo de IPs por nó.
- **Weave**: Fornece rede overlay com suporte à criptografia e políticas de rede. Pode ser integrado ao Calico para recursos adicionais de segurança.
- **Cilium**: Focado em segurança e desempenho, utiliza BPF para aplicar políticas de rede. Oferece recursos como balanceamento de carga, monitoramento e troubleshooting.
- **Kube-router**: Solução leve que usa BGP e IPVS para roteamento eficiente. Suporta políticas de rede e firewalls entre Pods.

**Em resumo:**
- Esses são apenas alguns dos plugins de rede mais populares no Kubernetes; a lista completa está no site oficial.
- A escolha do plugin depende das **necessidades do seu ambiente**, considerando vantagens e desvantagens de cada um.
- Prefira soluções já **validadas pela comunidade**, como Weave Net, Calico e Flannel.
- **Weave Net** é recomendado pela simplicidade na instalação e bons recursos.
- **Cilium** também é uma ótima opção, com comunidade ativa, recursos avançados e uso do BPF — destaque no ecossistema Kubernetes.

### Instalando o Weave Net

Agora que o cluster está inicializado, vamos instalar o Weave Net:

```bash
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
```

Você pode verificar o status dos componentes do cluster com o seguinte comando:

```bash
kubectl get pods -n kube-system

kubectl get nodes
```

Criando um Deployment para testar a comunicação entre os Pods:

```bash
kubectl create deployment nginx --image=nginx --replicas 3

kubectl get pods -o wide
```

#### Documentação
- [Kubernetes Doc - kubeadm join](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/)
- [Kubernetes Doc - kubeadm token](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-token/)
- [Kubernetes Doc - Network Plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/)
- [weave](https://github.com/weaveworks/weave)

## 8 - Visualizando mais informações sobre os nodes

Agora que já temos o nosso cluster com 03 nodes, nós podemos visualizar os detalhes de cada um deles, e assim entender cada detalhe:

```bash
## Ver a descrição do node
kubectl describe node k8s-1

## Visualizar detalhes dos outros dois nodes
kubectl get nodes k8s-2 -o wide
kubectl get nodes k8s-3 -o wide
```

### Desafio Day 5

Realizar a instalação do cluster Kubernetes utilizando o Kubeadm. Use a criatividade e teste diferentes plugins de redes.
- O mais importante é você ter um cluster Kubernetes funcionando e pronto para ser utilizado, e mais do que isso, é importante que você entenda como o cluster funciona e sinta-se confortável para realizar sua manutenção e a administração.

**Exemplo de cluster k8s criado no Vagrant**:
- Você pode acessar [este repositório](https://github.com/ludsilva/cluster-k8s-vagrant) para verificar o projeto com detalhes.