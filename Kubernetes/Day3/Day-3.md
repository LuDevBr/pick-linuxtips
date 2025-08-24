# Índice - Day 3

## 1 - O que é um Deployment

Um Deployment é um objeto que representa uma aplicação - ou seja, que nos permite definir o estado desejado para os Pods que compõem a aplicação.
- é um controlador de alto nível
- é responsável por gerenciar a implantação e atualização dos Pods que compõem uma aplicação
- é uma abstração que nos permite atualizar os Pods e também fazer o rollback para uma versão anterior caso algo dê errado
- é responsável por criar e gerenciar um replicaset.

Quando criamos um Deployment é possível definir o número de réplicas que queremos que ele tenha.
- ele garante que o número de Pods que ele está gerenciando seja o mesmo que o número de réplicas definido
- se um Pod morrer, o Deployment irá criar um novo Pod para substituí-lo

**Casos de uso**
- Criar Deployment para implementar um ReplicaSet.
- Atualizar `PodTemplateSpec` para declarar novo estado dos Pods.
- Fazer rollback para revisão anterior.
- Fazer scale up para suportar mais carga.
- Pausar o Deployment para aplicar múltiplas mudanças e retomá-lo depois.
- Usar o status do Deployment como indicador de falha.
- Limpar ReplicaSets antigos desnecessários.

#### Documentação
- [Kubernetes Documentation - Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Livro: Descomplicando o Kubernetes](https://github.com/badtuxx/DescomplicandoKubernetes/blob/main/pt/day-3/README.md#o-que-%C3%A9-um-deployment)

## 2 - Criando um Deployment através de um manifesto

Vamos utilizar um manifesto que cria um Deployment de nome `nginx-deployment`, e que possui 03 réplicas de um container com a imagem do `nginx`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-deployment
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-deployment
  strategy: {}
  template:
    metadata:
      labels:
        app: nginx-deployment
    spec:
      containers:
      - image: nginx
        name: nginx
        resources:
          limits:
            cpu: 0.5
            memory: 256Mi
          requests:
            cpu: 0.3
            memory: 64Mi
```

**Onde**
- Aqui nós estamos definindo que o tipo do objeto que estamos criando é um Deployment e a versão da API que estamos utilizando é a **apps/v1**.
    
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    ```
    
- Aqui nós estamos definindo o nome do Deployment, que é **nginx-deployment** e também estamos definindo as labels que serão adicionadas ao Deployment. As labels são utilizadas para identificar os objetos no Kubernetes:
    
    ```yaml
    metadata:
      labels:
        app: nginx-deployment
      name: nginx-deployment
    ```
    
- Aqui nós estamos definindo o número de réplicas que o Deployment irá ter. Nesse caso nós estamos definindo que o Deployment irá ter 3 réplicas.
    
    ```yaml
    spec:
      replicas: 3
    ```
    
- Aqui nós estamos definindo o **seletor** que será utilizado **para identificar os Pods que o Deployment irá gerenciar**. Nesse caso nós estamos definindo que o Deployment irá gerenciar os Pods que possuírem a label app: nginx-deployment.
    
    ```yaml
    selector:
      matchLabels:
        app: nginx-deployment
    ```
    
- Aqui nós estamos definindo a estratégia que será utilizada para atualizar os Pods. Nesse caso nós estamos deixando a estratégia padrão, que é a estratégia Rolling Update, ou seja, o Deployment irá atualizar os Pods um por um. Iremos entrar em detalhes sobre as estratégias mais para frente.
    
    ```yaml
    strategy: {}
    ```
    
- Aqui nós estamos definindo **o template que será utilizado para criar os Pods**. Nesse caso nós estamos definindo que o template irá utilizar a imagem **nginx** e que o nome do container será **nginx**. Também estamos definindo os limites de CPU e memória que poderão ser utilizados pelo container.
    
    ```yaml
    template:
      metadata:
        labels:
          app: nginx-deployment
      spec:
        containers:
        - image: nginx
          name: nginx
          resources:
            limits:
              cpu: 0.5
              memory: 256Mi
            requests:
              cpu: 0.25
              memory: 128Mi
    ```
    
### Comandos - aplicando o Deployment

```bash
## Iniciar o Deployment via manifesto
kubectl apply -f deployment.yaml

## Listar deployments
kubectl get deployments
kubectl get deployments.apps

## Ver os detalhes em yaml
kubectl get deployments.apps -o yaml

## Verificar se o Deployment foi criado
kubectl get deployments -l app=nginx-deployment

## Verificar os Pods que o Deployment está gerenciando
kubectl get pods -l app=nginx-deployment

## Ver replicasets
kubectl get replicasets
```

## 3 - Criando mais Deployments e vendo os detalhes

```bash
## Ver detalhes de um Deployment
kubectl describe deployments nginx-deployment

## Redirecionar para um arquivo yaml
kubectl get deployments.apps nginx-deployment -o yaml > temp.yaml

### Criar a partir do yaml
kubectl apply -f temp.yaml

## Criar um Deployment usando o terminal
kubectl create deployment --image nginx --replicas 3 nginx-deployment

### Deletar o deployment criado via terminal
kubectl delete deployments nginx-deployment

## Criar um arquivo YAML de um Deployment nginx-deployment terminal e flag --dry-run
kubectl create deployment --image nginx --replicas 3 nginx-deployment --dry-run=client -o yaml > deployment.yaml
```

## 4 - Como atualizar um Deployment

Quando é necessário fazer atualizações na aplicação, como mudar a versão do Nginx ou colocar o Deployment em uma Namespace específica:
- Entrar no manifesto, fazer as atualizações, salvar e aplicar

### Exemplo

- Criar um namespace

```bash
kubectl create namespace <nome-namespace>

## Exemplo
kubectl create namespace giropops
```

- Criar e um manifesto de um Deployment com o campo Namespace

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-deployment
  name: nginx-deployment
  namespace: giropops
spec:
  replicas: 10
  selector:
    matchLabels:
      app: nginx-deployment
  strategy: {}
  template:
    metadata:
      labels:
        app: nginx-deployment
    spec:
      containers:
      - image: nginx:1.15.0
        name: nginx
        resources:
          limits:
            cpu: 0.5
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi

```

**Comandos**

```bash
## Criar
kubectl apply -f deployment.yaml

## Visualizar deployments com namespace específico (giropops)
kubectl get deployments -n giropops 

## Visualizar Pods com o Namespace
kubectl get pods -n giropops 

## Direcionar para o yaml
kubectl create namespace giropops --dry-run=client -o yaml > exemplo-namespace.yaml

## Criando a namespace a partir de um arquivo
kubectl apply -f exemplo-namespace.yaml

## Visualizar ReplicaSets com o Namespace
kubectl get replicaset -n giropops 

## Describe
kubectl describe deployments -n giropops nginx-deployment
```

## 5 - Estratégias de atualizações de nossos Deployments

Necessidade de especificar qual o tipo de estratégia será usada para trocar Pods antigos por novos
- Há dois tipos de estratégias: **Rolling Update** e **Recreate**

### Estratégia Rolling Update

**Estratégia de atualização padrão do Kubernetes**, utilizada para atualizar os Pods de um Deployment de forma gradual, ou seja, ela atualiza um Pod por vez, ou um grupo de Pods por vez.
- pode especificar **maxUnavailable** e **maxSurge** para controlar o processo de atualização contínua
  
**Max Unavailable**
- define a quantidade máxima de Pods que podem ficar indisponíveis durante a atualização, ou seja, durante o processo de atualização
- o valor pode ser um número absoluto (por exemplo, 5) ou uma porcentagem dos Pods desejados (por exemplo, 10%)
  - o valor padrão é 25%.
  
**Max surge**
- define a quantidade máxima de Pods que podem ser criados a mais durante a atualização, ou seja, durante o processo de atualização

**Exemplo**

- Nesse caso, o restart vai atualizar de 2 em 2 (MaxUnavailable) e pode ter até 1 Pod a mais do que é pedido no arquivo (Max surge):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-deployment
  name: nginx-deployment
  namespace: giropops
spec:
  replicas: 10
  selector:
    matchLabels:
      app: nginx-deployment
  strategy: 
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 2
  template:
    metadata:
      labels:
        app: nginx-deployment
    spec:
      containers:
      - image: nginx:1.15.0
        name: nginx
        resources:
          limits:
            cpu: 0.5
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi

```

**Comandos**

```yaml
## Aplicar
kubectl apply -f deployment.yaml

## Descrever
kubectl describe deployments -n giropops nginx-deployment

## Ver os pods subindo
kubeclt get pods -n giropops

## Acompanhar o processo de atualização dos Pods
kubectl rollout status deployment -n giropops nginx-deployment

## Verificar se os pods foram atualizados
kubectl get pods -l app=nginx-deployment -n giropops -o yaml
```

### Estratégia Recriate

Estratégia de atualização que irá remover todos os Pods do Deployment e criar novos Pods com a nova versão da imagem.
- **Prós**: o deploy acontecerá rapidamente
- **Contras**: o serviço ficará indisponível durante o processo de atualização

Indicado usar essa estratégia em casos em que a aplicação não pode rodar com versões diferentes ao mesmo tempo.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-deployment
  name: nginx-deployment
  namespace: giropops
spec:
  replicas: 10
  selector:
    matchLabels:
      app: nginx-deployment
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: nginx-deployment
    spec:
      containers:
      - image: nginx:1.15.0
        name: nginx
        resources:
          limits:
            cpu: 0.5
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
~                           
```

**Comandos**

```bash
## Aplicar
kubectl apply -f deployment.yaml

## Listar o pods
kubectl get pods -l app=nginx-deployment -n giropops

## Acompanhar o status
kubectl rollout status deployment -n giropops nginx-deployment

```

#### Documentação
- [Kubernetes Documentation - Strategy](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy)

## 6 - Fazendo Rollback e conhecendo o Rollout

Quando se quer reverter uma implantação, ou seja, fazer o rollback:

```bash
## Aplicar uma mudança
kubectl apply -f deployment.yaml

## Verificar os pods
kubectl get pods -l app=nginx-deployment -n giropops

## Veriricar a versão da imagem do Nginx em um Pod
kubectl exec -it -n giropops nginx-deployment-7d9bcc6bc9-24c2j -- nginx -v

## Verificar o hostórico de revisões
kubectl rollout history deployment nginx-deployment -n giropops

## Para verificar os detalhes de uma revisão de um Deployment
kubectl rollout history deployment nginx-deployment --revision=6 -n giropops

## Fazer o rollback
kubectl rollout undo deployment nginx-deployment -n giropops

## Fazer o rollback para uma versão específica
kubectl rollout undo deployment nginx-deployment --to-revision=5 -n giropops
```

Outras opções do comando `kubectl rollout`

```bash
## Pausar os rollouts
kubectl rollout pause deployments -n giropops nginx-deployment

## Retomar os rollouts marcados como paused
kubectl rollout resume deployments -n giropops nginx-deployment

## Reiniciar um Deployment (restart)
kubectl rollout restart deployments -n webserver01 nginx-deployment

## Ver o status
kubectl rollout status deployment -n giropops nginx-deployment

## Fazer o scale via terminal
kubectl scale deployment -n giropops --replicas 5 nginx-deployment
kubectl get pods -l app=nginx-deployment -n giropops

```

**Removendo um Deployment**

```bash
## Remover um Deployment
kubectl delete deployment nginx-deployment

## Remover utilizando o manifesto
kubectl delete -f deployment.yaml
```

#### Documentação
- [Kubernetes Documentation - Updating a Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#updating-a-deployment)

## Desafio Day 3

Criar um manifesto de objeto *Deployment* com o maior número de campos.

- Criando uma namespace chamada `desafio`

```bash
kubectl create namespace desafio
```
- Arquivo `desafio-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: pcik-desafio3
  name: pick-desafio3
  namespace: desafio
spec:
  replicas: 5
  selector:
    matchLabels:
      app: pick-desafio3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: "40%"
      maxUnavailable: "40%"
  template:
    metadata:
      labels:
        app: pick-desafio3
    spec:
      containers:
      - image: nginx:1.19.0
        name: nginx
        resources:
          limits:
            cpu: 0.5
            memory: 256Mi
          requests:
            cpu: 0.3
            memory: 128Mi
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
      - image: alpine
        name: alpine
        args:
          - sleep
          - "500"
        resources:
          limits:
            cpu: 0.5
            memory: 128Mi
```