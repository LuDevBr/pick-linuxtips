# Índice - Day 6
- [Índice - Day 6](#índice---day-6)
  - [1 - O que são volumes](#1---o-que-são-volumes)
      - [Documentação](#documentação)
  - [2 - O StorageClass](#2---o-storageclass)
      - [Manifesto](#manifesto)
      - [Documentação](#documentação-1)
  - [3 - PV - PersistentVolume](#3---pv---persistentvolume)
      - [Documentação](#documentação-2)
  - [4 - PV - PersistentVolume com NFS](#4---pv---persistentvolume-com-nfs)
    - [Criar o StorageClass para o provisionador `nfs`](#criar-o-storageclass-para-o-provisionadornfs)
  - [5 - PVC - PersistentVolumeClaim](#5---pvc---persistentvolumeclaim)
    - [Passos](#passos)
    - [1, 2, 3, Testando…](#1-2-3-testando)
      - [Documentação](#documentação-3)
  - [Desafio Day 6](#desafio-day-6)
    - [StorageClass + Deployment + PV/PVC](#storageclass--deployment--pvpvc)

## 1 - O que são volumes

Os **Volumes** são diretórios acessíveis aos containers de um Pod, usados para **armazenamento de dados**. Eles evitam a perda de dados que ocorre quando um container reinicia ou falha.

**Tipos de volumes**
- **Efêmeros**: existem apenas durante a vida do Pod e são destruídos quando ele é finalizado.
- **Persistentes**: sobrevivem após o Pod ser destruído e são gerenciados separadamente.

**Como funcionam?**
- São definidos no campo `.spec.volumes` do Pod.
- A montagem nos containers é feita via `.spec.containers[*].volumeMounts`.
- Um container vê o sistema de arquivos da imagem mais os volumes montados.
- **Cada container deve declarar explicitamente onde montar o volume**.
- Volumes **não podem ser aninhados** ou conter links físicos para outros volumes.

#### Documentação
- [Kubernetes Doc - Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)

## 2 - O StorageClass

É um **objeto do Kubernetes** que define **classes de armazenamento** com diferentes características (como performance e custo). Permite o **provisionamento dinâmico** de PersistentVolumes (PVs) com base nos PersistentVolumeClaims (PVCs) dos usuários.
- Forma de automatizar a criação de PVs.

Para que serve?
- **Organizar e gerenciar tipos de armazenamento**, como discos rápidos ou baratos.
- Definir políticas de:
  - **Provisionamento**
  - **Retenção**
  - **Outras características específicas** de armazenamento

Como funciona
- Cada StorageClass usa um **provisionador** que cria os volumes dinamicamente.
- Os provisionadores podem ser:
  - **Internos** (do Kubernetes)
  - **Externos** (de provedores de nuvem ou storage)

**Exemplos de provisionadores**
- `kubernetes.io/aws-ebs`: AWS Elastic Block Store (EBS)
- `kubernetes.io/azure-disk`: Azure Disk
- `kubernetes.io/gce-pd`: Google Compute Engine (GCE) Persistent Disk
- `kubernetes.io/cinder`: OpenStack Cinder
- `kubernetes.io/vsphere-volume`: vSphere
- `kubernetes.io/no-provisioner`: Volumes locais
- `kubernetes.io/host-path`: Volumes locais

```bash
## Ver os Storage Classes disponíveis no seu cluster
kubectl get storageclass

kubectl describe storageclass.storage.k8s.io
```

#### Manifesto

Criar um novo `Storage Class` para o nosso cluster Kubernetes no kind, com o nome "local-storage", e vamos definir o provisionador como "kubernetes.io/host-path", que cria volumes PersistentVolume no diretório do host.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: giropops
provisioner: kubernetes.io/no-provisioner
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

**Comandos**
No EKS, o provisionador padrão é o `kubernetes.io/aws-ebs`, que cria volumes PersistentVolume no EBS da AWS

```bash
kubectl apply -f storageclass.yaml

## Ver os Storage Classes disponíveis no seu cluster
kubectl get storageclass

## Ver os detalhes do nosso Storage Class padrão
kubectl describe storageclass standard

## Obter detalhes de um determinado StorageClass
kubectl describe storageclass giropops
```

Lembrando que criamos esse `Storage Class` com o provisionador "kubernetes.io/no-provisioner", mas você pode criar um `Storage Class` com qualquer provisionador que você quiser, como o "kubernetes.io/aws-ebs", que cria volumes PersistentVolume no EBS da AWS.

#### Documentação
- [Kubernetes Doc - Storage classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Kubernetes Doc - Provisioner](https://kubernetes.io/docs/concepts/storage/storage-classes/#provisioner)

## 3 - PV - PersistentVolume

É um **objeto do Kubernetes** que representa um **recurso de armazenamento físico** no cluster. Pode ser provisionado manualmente por um administrador ou dinamivamente via StorageClass.

Pode ser:
- Um **disco local** no nó
- Um **armazenamento em rede (NAS/SAN)**
- Um **serviço de nuvem** como AWS EBS ou Google Persistent Disk

Oferece **armazenamento durável**, mantendo os dados mesmo após reinícios ou movimentação dos containers.

**Tipos de armazenamento usados como PV**
- **Armazenamento Local**
  - **HostPath**: Usa um diretório local do nó.
    - Simples e útil para testes/desenvolvimento
    - **Não recomendado** para produção (dados restritos ao nó)

- **Armazenamento em Rede**
  - **NFS**: Compartilha arquivos via rede entre múltiplos nós.
  - **iSCSI**: Conecta volumes de blocos via rede IP (ex: SAN).
  - **Ceph RBD**: Armazenamento distribuído, escalável e resiliente.
  - **GlusterFS**: Sistema de arquivos distribuído para compartilhamento entre nós.

- **Serviços de Nuvem**
    - AWS EBS
    - Google Cloud Persistent Disk
    - Azure Disk

Manifesto - criar o arquivo `pv.yaml`:

```yaml
apiVersion: v1 # Versão da API do Kubernetes
kind: PersistentVolume # Tipo de objeto que estamos criando, no caso um PersistentVolume
metadata: # Informações sobre o objeto
  name: meu-pv # Nome do nosso PV
  labels:
    storage: local
spec: # Especificações do nosso PV
  capacity: # Capacidade do PV
    storage: 1Gi # 1 Gigabyte de armazenamento
  accessModes: # Modos de acesso ao PV
    - ReadWriteOnce # Modo de acesso ReadWriteOnce, ou seja, o PV pode ser montado como leitura e escrita por um único nó
  persistentVolumeReclaimPolicy: Retain # Política de reivindicação do PV, ou seja, o PV não será excluído quando o PVC for excluído
  hostPath: # Tipo de armazenamento que vamos utilizar, no caso um hostPath
    path: "/mnt/data" # Caminho do hostPath, do nosso nó, onde o PV será criado
  storageClassName: giropops # Nome da classe de armazenamento que será utilizada
```

**Estrutura básica de um PV**
- **`kind: PersistentVolume`**: Define o tipo de recurso como um PersistentVolume.
- **`spec`**: Contém as configurações do PV:
  - **`capacity.storage`**: Define o tamanho do volume (ex: `1Gi`).
  - **`accessModes`**: Define os modos de acesso ao volume:
      - `ReadWriteOnce` – leitura e escrita por **um único nó**
      - `ReadOnlyMany` – somente leitura por **vários nós**
      - `ReadWriteMany` – leitura e escrita por **vários nós**
  - **`persistentVolumeReclaimPolicy`**: Política de descarte do PV após o PVC ser removido:
        - `Retain` – mantém o volume
        - `Recycle` – limpa o volume
        - `Delete` – apaga o volume

Tipos de armazenamento suportados
- **`hostPath`**: Usa diretório local do nó – útil para testes, **não recomendado em produção.**
- **`nfs`**: Compartilhamento de arquivos em rede.
- **`iscsi`**: Acesso a volumes de bloco via IP (ex: SAN).
- **`csi`**: Interface para integrar **soluções de armazenamento de terceiros** (ex: AWS EBS, Azure Disk).
- **`cephfs`**: Sistema de arquivos distribuído.
- **`local`**: Volume local com caminho definido – diferente do `hostPath` por ser recurso **nativo do Kubernetes**.
- **`fc` (Fibre Channel)**: Conexão via **rede de fibra óptica** para armazenamento de blocos.

**Comandos**

```bash
## Listar todos os pvs do cluser
kubectl get pv -A

## Criar o PV
kubectl apply -f pv.yaml

## Ver detalhes do pv
kubectl describe pv meu-pv
```

#### Documentação
- [Kubernetes Doc - Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)


## 4 - PV - PersistentVolume com NFS

Criando um compartilhamento NFS:

```bash
## Instalar os pacotes nfs-kernel-server e nfs-common
sudo apt-get install nfs-kernel-server nfs-common

## Criar o diretório do compartilhamento
mkdir /mnt/nfs

## Editar o arquivo /etc/exports
sudo vi /etc/exports
> /mnt/nfs *(rw,sync,no_root_squash,no_subtree_check)

```

**Onde**:
- `/mnt/nfs`: é o diretório que você deseja compartilhar.
- `*`: permite que qualquer host acesse o diretório compartilhado. Para maior segurança, você pode substituir * por um intervalo de IPs ou por IPs específicos dos clientes que terão acesso ao diretório compartilhado. Por exemplo, 192.168.1.0/24 permitiria que todos os hosts na sub-rede 192.168.1.0/24 acessassem o diretório compartilhado.
- `rw`: concede permissões de leitura e gravação aos clientes.
- `sync`: garante que as solicitações de gravação sejam confirmadas somente quando as alterações tiverem sido realmente gravadas no disco.
- `no_root_squash`: permite que o usuário root em um cliente NFS acesse os arquivos como root. Caso contrário, o acesso seria limitado a um usuário não privilegiado.
- `no_subtree_check`: desativa a verificação de subárvore, o que pode melhorar a confiabilidade em alguns casos. A verificação de subárvore normalmente verifica se um arquivo faz parte do diretório exportado.

**Continuando….**

```bash
# Informe o NFS que o diretório /mnt/nfs está disponível para ser compartilhado
sudo exportfs -ar

# Verifique se o NFS foi montado
showmount -e
```

### Criar o StorageClass para o provisionador `nfs`

Vamos criar o arquivo `storageclass-nfs.yaml`:

```yaml
apiVersion: storage.k8s.io/v1 # Versão da API do Kubernetes
kind: StorageClass # Tipo de objeto que estamos criando, no caso um StorageClass
metadata: # Informações sobre o objeto
  name: nfs # Nome do nosso StorageClass
provisioner: kubernetes.io/no-provisioner # Provisionador que será utilizado para criar o PV
reclaimPolicy: Retain # Política de reivindicação do PV, ou seja, o PV não será excluído quando o PVC for excluído
volumeBindingMode: WaitForFirstConsumer
parameters: # Parâmetros que serão utilizados pelo provisionador
  archiveOnDelete: "false" # Parâmetro que indica se os dados do PV devem ser arquivados quando o PV for excluído
```

O Kubernetes não possui um provisionador `nfs` nativo, então não é possível fazer com que o provisionador `kubernetes.io/no-provisioner` crie um PV utilizando um servidor NFS automaticamente. Para que isso seja possível, precisamos utilizar um provisionador `nfs` externo. No nosso caso, iremos criar o PV manualmente.

Criar um novo arquivo chamado `pv-nfs.yaml`:

```yaml
apiVersion: v1 # Versão da API do Kubernetes
kind: PersistentVolume # Tipo de objeto que estamos criando, no caso um PersistentVolume
metadata: # Informações sobre o objeto
  name: meu-pv-nfs # Nome do nosso PV
  labels:
    storage: nfs # Label que será utilizada para identificar o PV
spec: # Especificações do nosso PV
  capacity: # Capacidade do PV
    storage: 1Gi # 1 Gigabyte de armazenamento
  accessModes: # Modos de acesso ao PV
    - ReadWriteOnce # Modo de acesso ReadWriteOnce, ou seja, o PV pode ser montado como leitura e escrita por um único nó
  persistentVolumeReclaimPolicy: Retain # Política de reivindicação do PV, ou seja, o PV não será excluído quando o PVC for excluído
  nfs: # Tipo de armazenamento que vamos utilizar, no caso o NFS
    server: IP_DO_SERVIDOR_NFS # Endereço do servidor NFS
    path: "/mnt/nfs" # Compartilhamento do servidor NFS
  storageClassName: giropops # Nome da classe de armazenamento que será utilizada
```

**Comandos**

```bash
kubectl apply -f pv-nfs.yaml
```

## 5 - PVC - PersistentVolumeClaim

O **PVC (PersistentVolumeClaim)** é uma solicitação de armazenamento feita por usuários ou aplicações no cluster Kubernetes. Ele permite especificar **tamanho, tipo de armazenamento e modo de acesso** desejado.

O PVC funciona como uma **"assinatura"** que reivindica um **PV (PersistentVolume)** compatível. O Kubernetes realiza automaticamente a **associação entre o PVC e um PV** disponível, garantindo a alocação correta do armazenamento.

O uso de PVC **abstrai os detalhes do tipo de armazenamento**, facilitando a portabilidade entre diferentes ambientes e provedores. Ele permite a **flexibilidade na solicitação de volumes** com diferentes características.

Todo PVC é associado a:
- Um **StorageClass**, que define diferentes **classes de armazenamento** disponíveis no cluster, ou
- Um **PersistentVolume**, que representa o **volume físico ou lógico** disponível para uso.

### Passos

Criar um arquivo chamado `pvc.yaml`

```yaml
apiVersion: v1 # versão da API do Kubernetes
kind: PersistentVolumeClaim # tipo de recurso, no caso, um PersistentVolumeClaim
metadata: # metadados do recurso
  name: meu-pvc # nome do PVC
spec: # especificação do PVC
  accessModes: # modo de acesso ao volume
    - ReadWriteOnce # modo de acesso RWO, ou seja, somente leitura e escrita por um nó
  resources: # recursos do PVC
    requests: # solicitação de recursos
      storage: 1Gi # tamanho do volume que ele vai solicitar
  storageClassName: giropops # nome da classe de armazenamento que será utilizada
  selector: # seletor de labels
    matchLabels: # labels que serão utilizadas para selecionar o PV
      storage: nfs # label que será utilizada para selecionar o PV
```

**Onde**:
- **`accessModes`**: Define o modo de acesso ao volume:
  - `ReadWriteOnce (RWO)`: leitura e escrita por um único nó.
  - `ReadOnlyMany (ROX)`: somente leitura por múltiplos nós.
  - `ReadWriteMany (RWX)`: leitura e escrita por múltiplos nós.
- **`resources`**: Especifica os recursos solicitados, como o **tamanho do volume** (ex: `1Gi`).
- **`storageClassName`**: Define a **classe de armazenamento** associada ao PVC.
- **`selector`**: Utiliza **labels** para selecionar um **PersistentVolume (PV)** específico a ser associado ao PVC.

Agora, vamos criar o PVC:

```bash
## Apply
kubectl apply -f pvc.yaml

## Conferir se o pvc foi criado corretamente
kubectl get pvc

## Ver detalhes
kubectl describe pvc meu-pvc
```

Vamos criar um Pod para vincular ao PVC:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: meu-pvc
      mountPath: /usr/share/nginx/html
  volumes:
  - name: meu-pvc
    persistentVolumeClaim:
      claimName: meu-pvc
```

O que estamos fazendo aqui é basicamente o seguinte:
- Criando um Pod com o nome `nginx-pod`;
- Utilizando a imagem `nginx:latest` como base;
- Expondo a porta 80;
- Definindo um volume chamado `meu-pvc` e montando ele no caminho `/usr/share/nginx/html` dentro do container;
- Por fim, definindo que o volume `meu-pvc` é um `PersistentVolumeClaim` e que o nome do PVC é `meu-pvc`.

**Comandos**

```bash
## Criar o pod
kubectl apply -f pod.yaml

## Ver se o PVC foi vinculado ao PV
kubectl get pvc

## Ver a saída do get pv
kubectl get pv

## Ver se o Pod está utilizando o volume
kubectl describe pod nginx-pod
```

### 1, 2, 3, Testando…

Vamos criar um arquivo HTML simples no diretório `/mnt/data` do nosso servidor NFS

```bash
## Criar o arquivo
echo "<h1>GIROPOPS STRIGUS GIRUS</h1>" > /mnt/data/index.html

## Verificar se o arquivo foi criado
kubectl exec -ti nginx-pod -- ls /usr/share/nginx/html

## Fazer um curl dentro do Pod
kubectl exec -ti nginx-pod -- curl localhost
```

#### Documentação
- [Kubernetes Doc - Configure a Pod to Use a PersistentVolume for Storage](https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/)
- [Livro: Descomplicando o Kubernetes - Day 6](https://github.com/badtuxx/DescomplicandoKubernetes/tree/main/pt/day-6#inicio-da-aula-do-day-6)

## Desafio Day 6

A sua lição de casa é criar um deployment do Nginx, que possua um volume montado no `/usr/share/nginx/html`.

### StorageClass + Deployment + PV/PVC

**Exemplo usando `hostPath`:**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: desafio
provisioner: kubernetes.io/no-provisioner
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nginx-volume-pv
  labels:
    type: local
spec:
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath: 
    path: "/tmp/nginx-data"
  storageClassName: desafio

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nginx-volume-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  storageClassName: desafio
  selector:
    matchLabels:
      type: local

---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-deployment-desafio
  name: nginx-deployment-desafio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-deployment-desafio
  strategy: 
    type: Recreate
  template:
    metadata:
      labels:
        app: nginx-deployment-desafio
    spec:
      containers:
      - image: nginx:1.20.1
        name: nginx
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        volumeMounts:
        - mountPath: /usr/share/nginx/html
          name: nginx-volume-pvc
        resources:
          requests:
            memory: 64Mi
            cpu: 0.3
          limits:
            memory: 128Mi
            cpu: 0.5
        startupProbe:
          tcpSocket:
            port: 80
          initialDelaySeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
        livenessProbe:
          tcpSocket:
            port: 80
          initialDelaySeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
          successThreshold: 1
        readinessProbe:
          httpGet:
            tcpSocket:
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 10
          failureThreshold: 3
          successThreshold: 1
      volumes:
      - name: nginx-volume-pvc
        persistentVolumeClaim:
          claimName: nginx-volume-pvc
```

- OBS: como o `hostPath` usa um diretório local do node, temos só um pod (uma réplica) no exemplo - poderíamos também forçar os pods subir no mesmo node. Além disso, para referenciar um volume local usando o kind e manter mesmo quando o cluster for excluído, foi gerado um novo arquivo `kind.yaml`. Você pode utilizar os **Extra Mounts** do kind, conforme [documentação oficial](https://kind.sigs.k8s.io/docs/user/configuration/#extra-mounts).