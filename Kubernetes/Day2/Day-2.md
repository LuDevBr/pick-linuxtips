# Índice - Day 2

## 1 - O que é um pod

O Pod a menor unidade de computação dentro de um cluster Kubernetes

⚠️ **Atenção**: Um pod não é igual a um container, hein!

Podemos entender o Pod como uma “caixinha” que contém um ou mais containers que compartilham do mesmo namespace (ex: endereçamento de rede)
- Esses containers compartilham os mesmos recursos do Pod, como por exemplo, o IP, o namespace, o volume, etc

Em clusters Kubernetes são usados, geralmente, de duas maneiras
- Pods que executam apenas um container
- Pods que executam vários containers que trabalham juntos

Comunicação entre containers:
- dois containers no mesmo pod → a comunicação é local, mesma interface - têm apenas 1 endereço de rede
- dois pods diferentes → comunicação entre eles via IP

#### Documentação
- [Kubernetes Documentation - Pods](https://kubernetes.io/docs/concepts/workloads/pods/)

## 2 - Os sensacionais kubectl get pods e kubectl describe pods

O comando `kubectl get` mostra as informações mais importantes sobre os recursos

**Criando o pod através do comando** `kubectl run`

```bash
## Criar um pod com comando
kubectl run giropops --image=nginx --port=80

## Ver o pod criado
kubectl get pods

## Listar todos os pods
kubectl get pods -A

## Ver os Pods em execução em todas as namespaces,
kubectl get pods --all-namespaces

## Ver de uma namespace específica
kubectl get pods -n <namespace>

## Ver datalhes do pod em formato YAML
kubectl get pods <nome-do-pod> -o yaml
kubectl get pods giropops -o yaml

## Ver detalhes do pod em formato JSON
kubectl get pods <nome-do-pod> -o json
kubectl get pods giropops -o json

## Ver mais detalhes (IP e node)
kubectl get pods <nome-do-pod> -o wide
kubectl get pods giropops -o wide

## Ver pelas labels - ex: run
kubectl get pods -L run

## Remover o pod
kubectl delete pods giropops
```

Já o `kubectl describe` mostra uma descrição detalhada dos recursos selecionados, incluindo recursos relacionados, como eventos ou controladores.

```bash
## Ver detalhes do pod
kubectl describe pods <nome-do-pod>
kubectl describe pods giropops
```

#### Documentação
- [Kubernetes Documentation - Get](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#get)
- [Kubernetes Documentation - Describe](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#describe)

## 3 - Conhecendo o kubectl attach e kubectl exec

Vamos criar 2 pods - usando comando `run`:
- 1 Nginx - strigus
- 1 alpine - girus

```bash
## Criar um pod Nginx
kubectl run strigus --image nginx --port 80

## Pegar o podIP
kubectl get pods strigus -o yaml
## EX: 10.244.1.2

## Criar um  com interação - bash
kubectl run girus --image alpine -ti -- sh
apk add curl
>> curl <IP> ## curl 10.244.1.2
```

O comando `attach` é usado para se conectar a um container que está rodando dentro de um Pod:

```bash
## Para voltar ao bash do pod
kubectl attach girus -c girus -ti
```

O comando `exec` é usado para executar comandos dentro de um container que está rodando dentro de um Pod:

```bash
## Exemplo
kubectl exec -ti <nome-do-pod> -c <nome-do-container> -- bash

## Executar o comando bash dentro do container - Nginx
kubectl exec -ti strigus -- bash
```

#### Documentação
- [Kubernetes Documentation - Run](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#run)
- [Kubernetes Documentation - Attach](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#attach)
- [Kubernetes Documentation - Exec](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#exec)

## 4 - Criando nosso pod multicontainer utilizando um manifesto

O arquivo `YAML` descreve o estado desejado de um recurso é chamado de **manifesto**.

**Gerando o manifesto** com o *--dry-run*:

```bash
kubectl run girus-1 --image alpine --dry-run=client -o yaml > pod.yaml
```

**Conteúdo do YAML**

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: girus-1
  name: girus-1
spec:
  containers:
  - image: alpine
    name: girus-1
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```

**Explicação**
- `apiVersion: v1` - versão da API do Kubernetes
- `kind: Pod`- tipo do objeto que estamos criando
- `metadata:` - metadados do Pod
- `name: girus-1` - nome do Pod que estamos criando
- `labels:` - labels do Pod
- `run: girus-1` - label run com o valor giropops
- `spec:` - especificação do Pod
- `containers:` - containers que estão dentro do Pod
- `name: girus-1` - nome do container
- `image:` - imagem do container
- `resource`: - se tive alguma limitação de recursos
- `dnsPolicy` - como vai ser o DNS (resolve primeiro dentro do cluster)
- `restartPolicy` - se o pod vai restartar ou não
- `status` - infos da execução

**Rodando o manifesto**

```yaml
##Criar um novo pod
kubectl create -f pod.yaml

## Crir um novo e aplicar modificações
kubectl apply -f pod.yaml
```

**Novo manisfesto - com Nginx**

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: girus
    service: webservers
  name: girus
spec:
  containers:
  - image: nginx
    name: girus
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
```

**Modificar o YAML colocando um container novo**

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp:
  labels:
    run: girus
    service: webservers
  name: girus
spec:
  containers:
  - image: nginx
    name: nginx
    resources: {}
  - image: alpine
    name: strigus
    args:
      - sleep ## processo em 2 plano para que o container não pare de rodar
      - "600"
  dnsPolicy: ClusterFirst
  restartPolicy: Always

```

**Aplicando…**

```bash
kubectl delete -f pod.yaml

kubectl apply -f pod.yaml

kubectl get pods
```

**Ver os logs**

```bash
kubectl logs <nome_do_pod>
kubectl logs girus

## Logs em tempo real
kubectl logs girus -f

## Ver logs por container
kubectl logs girus -c strigus
```

#### Documentação
- [Kubernetes Documentation - Create](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#create)
- [Kubernetes Documentation - Apply](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#apply)
- [Kubernetes Documentation - Logs](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#logs)

## 5 - Limitando o consumo de recursos de CPU e memória

É muito importante colocar limites de utilização de recursos de um pod (especificamente dos containers rodando dentro do Pod), principalmente memória e CPU

Para isso, vamos criar um arquivo yaml chamado `pod-limitado.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: new-giropops
  name: new-giropops
spec:
  containers:
  - image: ubuntu
    name: ubuntu
    args:  
    - sleep
    - "1800"
   resources:
     limits:
       cpu: "0.5"
       memory: "128Mi"
     requests:
       cpu: "0.3"
       memory: "64Mi"
 dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```

**Onde**
- `resources:` - recursos que estão sendo utilizados pelo container
  - `limits:` - limites máximo de recursos que o container pode utilizar
    - `memory: "128Mi"` - limite de memória que está sendo utilizado pelo container, no caso 128 megabytes no máximo
    - `cpu: "0.5"` # limite máxima de CPU que o container pode utilizar, no caso 50% de uma CPU no máximo
  - `requests:` - recursos garantidos ao container quando ele subir
    - `memory: "64Mi"` - memória garantida ao container, no caso 64 megabytes
    - `cpu: "0.3"` - CPU garantida ao container, no caso 30% de uma CPU


💡 *O valor `M` é usado para definir o limite de memória em megabytes no Docker, que utiliza o sistema de **unidades decimais**. Então, se você estiver utilizando o Docker, você pode usar o valor `M`, mas se você estiver utilizando o Kubernetes, você deve usar o valor `Mi` para definir o limite de memória, pois ele usa o sistema de **unidades binárias**.*

**Aplicando…**

```bash
kubectl apply -f pod.yaml

kubectl get pods

kubectl describe pods new-giropops

## Entrar no container e fazer teste de stress
kc exec -ti new-giropops -- bash
> apt install stress-ng
> stress-ng --vm-bytes 64M --vm 1
> stress --vm 1 --cpu 1
```

#### Documentação
- [Kubernetes Documentation - Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

## 6 - Configurando o nosso primeiro volume EmptyDir

O EmptyDir é um tipo de volume que é criado no momento em que o Pod é criado, e ele é destruído quando o Pod é destruído, ou seja, **ele é um volume temporário**
- todos containers no Pod podem ler e gravar no volume **emptyDir**
- quando um Pod é destruído os dados em **emptyDir** são excluídos permanentemente

Cenário de uso comum
- dois containers em um Pods e a necessidade compartilhar um volume entre os containers

Vamos criar o arquivo `pod-emptydir.yaml` com um volume do tipo **emptyDir**, com o tamanho de 256MB e de nome *primeiro-emptydir*

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: giropops
  name: giropops
spec:
  containers:
  - image: nginx
    name: webserver
    volumeMounts: # lista de volumes que serão montados no container
    - mountPath: /giropops
      name: primeiro-emptydir
    resources:
      limits:
        cpu: "0.5"
        memory: "128Mi"
      requests:
        cpu: "0.3"
        memory: "64Mi"
        
  dnsPolicy: ClusterFirst
  restartPolicy: Always
  volumes: # lista de volumes
  - name: primeiro-emptydir  # nome do volume
    emptyDir: # tipo do volume
      sizeLimit: 256Mi # tamanho máximo do volume

```

**Onde**
- `volumeMounts:` - lista de volumes que serão montados no container
  - `- name:` primeiro-emptydir - nome do volume
  - `mountPath: /giropops -` diretório onde o volume será montado

- `volumes:` - lista de volumes
  - `- name: primeiro-emptydir` - nome do volume
  - `emptyDir:` - tipo do volume
  - `sizeLimit: 256Mi` - tamanho máximo do volume

**Aplicando**

```bash
kubectl apply -f pod.yaml

kubectl get pods

kubectl describe pods giropops

## Acessar o container
kubectl exec -ti giropops -- bash
> cd giropops
> touch FUNCIONAAA
```

#### Documentação
- [Kubernetes Documentation - EmptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)

## Desafio Day 2

Criar um manifesto de um Pod com o maior número de campos e utilizar os parâmetros aprendidos.

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    enviroment: test
    app: desafioDay2
    run: desafio-pick
  name: desafio-pick
spec:
  containers:
  - image: httpd
    name: apache
    ports:
    - containerPort: 80
      name: http
      protocol: tcp
    resources:
      limits:
        cpu: "0.5"
        memory: "256Mi"
      requests:
        cpu: "0.3"
        memory: "128Mi"
  - image: debian
    name: debian
    volumeMounts:
    - mountPath: /desafio
      name: desafio-emptydir
    command: ["sleep"]
    args: ["600"]
    resources:
      limits:
        cpu: "0.5"
        memory: "256Mi"
      requests:
        cpu: "0.3"
        memory: "128Mi"
  volumes:
  - name: desafio-emptydir
    emptyDir:
      sizeLimit: 256Mi
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```