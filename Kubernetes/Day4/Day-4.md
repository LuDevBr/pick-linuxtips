# Índice - Day 4

## 1 - O que é um ReplicaSet?

O ReplicaSet tem como objetivo **manter um conjunto estável de réplicas de Pods em execução** em qualquer momento. Sua função é assegurar que as réplicas de pods idênticos estejam em um número desejado.

Quando criamos um Deployment, o Kubernetes cria um ReplicaSet para criar e fazer o gerenciamento das réplicas dos Pods em nosso cluster. É o responsável por ficar observando os Pods e garantir o número de réplicas que nós definimos no Deployment.
- ⚠️ É possível criar um ReplicaSet sem um Deployment, mas não é uma boa prática.
- Ele não tem a capacidade de fazer o gerenciamento de versões dos Pods e nem do `RollingUpdate`.
  
Quando estamos fazendo a atualização de uma versão de um Pod com o Deployment, o Deployment cria um novo ReplicaSet para fazer o gerenciamento das réplicas dos Pods e quando a atualização termina, o Deployment remove as réplicas do ReplicaSet antigo e deixa apenas as réplicas do ReplicaSet novo.
- ele não remove o ReplicaSet antigo, ele deixa ele lá, pois ele pode ser usado para fazer um Rollback da versão do Pod caso algo dê errado

Quando precisamos fazer o Rollback de uma atualização em nossos Pods, o Deployment somente muda o ReplicaSet que está sendo usado para fazer o gerenciamento das réplicas dos Pods, passando a utilizar o ReplicaSet antigo.


#### Documentação
- [Kubernetes Documentation - ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)

## 2 - O Deployment e o ReplicaSet

O Deployment é um objeto que cria um ReplicaSet e o ReplicaSet é um objeto que cria um Pod.
- o Deployment gerencia atualizações e o ciclo de vida de aplicações, enquanto o ReplicaSet garante o número desejado de réplicas de Pods em execução no Kubernetes.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-deployment
  name: nginx-deployment
spec:
  replicas: 1
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
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
```

- **Comandos**

```bash
kubectl apply -f nginx-deployment.yaml

kubectl get deployments

## Listar os pods
kubectl get pods

## Listar os replicasets
kubectl get replicasets

### Describe replicasets
kubectl describe rs

## Fazer o rollback
kubectl rollout undo deployment nginx-deployment 
```

*OBS: O nome do ReplicaSet responsável pelos pods em execução é formado pelo Hash do RS + nome do deployment.*

#### Documentação
- [Kubernetes Documentation - Dpeloyment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Documentation - ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)

## 3 - Criando o nosso ReplicaSet

*Criando o manifesto* com o arquivo `nginx-replicaset.yaml`:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  labels:
    app: nginx-app
  name: nginx-replicaset
spec:
  replicas: 5
  selector:
    matchLabels:
      app: nginx-app
  template:
    metadata:
      labels:
        app: nginx-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.17.0
        resources:
          limits:
            cpu: 0.5
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
```

**Onde**:
- A principal diferença é que agora nós estamos usando o `kind: ReplicaSet` e não o `kind: Deployment`, até o `APIVersion` é o mesmo.

**Comandos**

```bash
## Deploy via manifesto
kubectl apply -f nginx-replicaset.yaml

## Listar os Pods que estão rodando
kubectl get pods

## Describe
kubectl describe replicaset nginx-replicaset

## Apagar os pods - para atualizar o campo spec
kubectl delete pod nginx-replicaset-<id_do_pod>

## Deletar o replicaset
kubectl delete replicaset <nome_do_rs>
kubectl delete replicaset nginx-replicaset
```

Após a execução do manifesto, se alterar algum campo em `spec.template.spec`, os Pods não serão atualizados automaticamente - ou seja, não vai fazer o rollout para a nova versão.
- o ReplicaSet não faz o gerenciamento de versões, ele apenas garante que o número de réplicas do Pod esteja sempre ativo

⚠️  **ATENÇÃO**: *Não gerencie o **ReplicaSet** diretamente, use sempre um **Deployment**.*

## 4 - O que é um DaemonSet

O DaemonSet é um objeto que cria um Pod e esse Pod é um objeto que fica rodando em todos os nodes do cluster
- é com DaemonSet que nós conseguimos **garantir que teremos pelo menos um Pod rodando em cada node do cluster**
- e podemos garantir que ao menos uma réplica estará rodando em cada um dos nós

O DaemonSet é muito útil para executar Pods que precisam ser executados em todos os nós do cluster, como por exemplo, um Pod que faz o monitoramento de logs, ou um Pod que faz o monitoramento de métricas.

Alguns casos de uso de `DaemonSets` são:
- Execução de agentes de monitoramento, como o `Prometheus Node Exporter` ou o `Fluentd`.
- Execução de um proxy de rede em todos os nós do cluster, como `kube-proxy`, `Weave Net`, `Calico` ou `Flannel`.
- Execução de agentes de segurança em cada nó do cluster, como `Falco` ou `Sysdig`.

#### Documentação
- [Kubernetes Documentation - DeamonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)

## 5 - Criando o nosso DaemonSet

Vamos para o nosso primeiro exemplo, vamos criar um `DaemonSet` que vai garantir que todos os nós do cluster executem uma réplica do `Pod` do `node-exporter`, que é um exporter de métricas do **Prometheus**.

- Criar um arquivo chamado `node-exporter-daemonset.yaml`

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app: node-exporter-daemonset
  name: node-exporter-daemonset
spec:
  selector:
    matchLabels:
      app: node-exporter-daemonset
  template:
    metadata:
      labels:
        app: node-exporter-daemonset
    spec:
      hostNetwork: true
      containers:
        - name: node-exporter
          image: prom/node-exporter:latest
          ports:
          - containerPort: 9100
            hostPort: 9100
          volumeMounts:
          - name: proc
            mountPath: /host/proc
            readOnly: true
          - name: sys
            mountPath: /host/sys # <-- Correção aqui
            readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
```

Um **DaemonSet** precisa obrigatoriamente de ter os campos:
- apiVersion
- kind
- metadados

```bash
## Criar o DaemonSet via manifesto
kubectl apply -f node-exporter-daemonset.yaml

## Verificar se o DaemonSet foi criado
kubectl get daemonset

## Verificar os Pods que o DaemonSet está gerenciando
kubectl get pods -l app=node-exporter

## Describe
kubectl describe daemonset node-exporter-daemonset
kubectl describe ds node-exporter-daemonset

## Escalar o cluster, aumentando o numero de nos - usando ELS
eksctl scale nodegroup --cluster=eks-cluster --nodes 5 --name eks-cluster-nodegroup

## Verificar os pods
kubectl get pods -o wide -l app=node-exporter

## Verificar se o DaemonSet está gerenciando um nó
kubectl describe daemonset node-exporter-<node>

## Removento o deamonset
kubectl delete daemonset node-exporter-deamonset
```

## 6 - Porque não usamos o kubectl create agora

- Não é possível fazer a criação do DaemonSet e ReplicaSet com o `create`

## 7 - O que são as Probes no Kubernetes

As probes são uma forma de monitorar o Pod e saber se ele está em um estado saudável ou não. Com elas é possível assegurar que seus Pods estão rodando e respondendo de maneira correta, e mais do que isso, que o Kubernetes está testando o que está sendo executado dentro do seu Pod.
- A probes funcionam por Container.

Hoje nós temos disponíveis três tipos de probes: a **livenessProbe**, a **readinessProbe** e a **startupProbe**.
- É necessário ao menos usar o **Liveness** e o **Readness**.

#### Documentação
- [Kubernetes Documentation - Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)

## 8 - Liveness Probe

É a probe de **verificação de integridade**, e o que ela faz é verificar se o que está rodando dentro do Pod está saudável. Ou seja, é verificar se o que está rodando dentro do Pod está vivo.

![pod-morena-ta-viva](../../img/morena-pod.webp)

O que fazemos é criar uma forma de testar se o que temos dentro do Pod está respondendo conforme esperado. Se por acaso o teste falhar, o Pod será reiniciado.
- Se um container falhar repetidamente em sua verificação de atividade, o kubelet reinicia o container.

Campos para controlar o comportamento das verificações de inicialização, atividade e prontidão:
- `initialDelaySecond`: tempo de espera antes da primeira checagem.
- `periodSeconds`: frequência em segundos das checagens. Valor padrão é `10`, e o valor mínimo é `1`.
- `timeoutSeconds`: tempo limite em segundos para considerar falha. O valor padrão é `1` e o valor mínimo é `1`.
- `successThreshold`: sucessos consecutivos necessários após uma falha. O valor padrão é `1`.
- `failureThreshold`: falhas consecutivas para considerar o container indisponível. O Kubernetes vai considerar que a verificação geral falhou: o container não está ready/healthy/live. Valor padrão é `3`, e o valor mínimo é `1`.
- `terminationGracePeriodSeconds`: tempo em segundos de espera antes de forçar o encerramento do container. Valor default é `30`, e o valor mínimo é `1`.

### TCP liveness probe

Criar o arquivo `nginx-deployment.yaml`:

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        livenessProbe: # Aqui é onde vamos adicionar a nossa livenessProbe
          tcpSocket: # Aqui vamos utilizar o tcpSocket, onde vamos se conectar ao container através do protocolo TCP
            port: 80 # Qual porta TCP vamos utilizar para se conectar ao container
          initialDelaySeconds: 10 # Quantos segundos vamos esperar para executar a primeira verificação
          periodSeconds: 10 # A cada quantos segundos vamos executar a verificação
          timeoutSeconds: 5 # Quantos segundos vamos esperar para considerar que a verificação falhou
          failureThreshold: 3 # Quantos falhas consecutivas vamos aceitar antes de reiniciar o container
```

**Explicação**
- queremos testar se o `Pod` está respondendo através do protocolo TCP, através da opção `tcpSocket`, na porta 80 que foi definida pela opção `port`
- definimos que queremos esperar 10 segundos para executar a primeira verificação utilizando `initialDelaySeconds`
- por conta da `periodSeconds` falamos que queremos que a cada 10 segundos seja realizada a verificação
- caso a verificação falhe, vamos esperar 5 segundos, por conta da `timeoutSeconds`, para tentar novamente,
- e utilizamos o `failureThreshold`, se falhar mais 3 vezes, vamos reiniciar o `Pod`.

### Teste de falha

Alterar a porta para 81:

```yaml
        livenessProbe: 
          tcpSocket: 
            port: 81 # Qual porta TCP vamos utilizar para se conectar ao container
          initialDelaySeconds: 10 
          periodSeconds: 10 
          timeoutSeconds: 5 
          failureThreshold: 3
```

### liveness HTTP request

Usar o `httpGet` para tentar acessar um endpoint dentro do nosso `Pod`.

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        livenessProbe: # Aqui é onde vamos adicionar a nossa livenessProbe
          httpGet: # Aqui vamos utilizar o httpGet, onde vamos se conectar ao container através do protocolo HTTP
            path: / # Qual o endpoint que vamos utilizar para se conectar ao container
            port: 80 # Qual porta TCP vamos utilizar para se conectar ao container
          initialDelaySeconds: 10 # Quantos segundos vamos esperar para executar a primeira verificação
          periodSeconds: 10 # A cada quantos segundos vamos executar a verificação
          timeoutSeconds: 5 # Quantos segundos vamos esperar para considerar que a verificação falhou
          failureThreshold: 3 # Quantos falhas consecutivas vamos aceitar antes de reiniciar o container
```

**Explicação**
- Agora estamos utilizando o `httpGet` para testar se o `Nginx` está respondendo corretamente através do protocolo HTTP, e para isso, estamos utilizando o endpoint `/` e a porta 80.
- opção `path`, que é o endpoint que vamos utilizar para testar se o `Nginx` está respondendo corretamente, e claro, a `httpGet` é a forma como iremos realizar o nosso teste, através do protocolo HTTP.


**Comandos**

```bash
kubectl apply -f nginx-deployment.yaml

kubectl get deployments

kubectl describe pod nginx-deployment-<hs-do-pod>
```

### Teste de falha

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        livenessProbe: # Aqui é onde vamos adicionar a nossa livenessProbe
          httpGet: # Aqui vamos utilizar o httpGet, onde vamos se conectar ao container através do protocolo HTTP
            path: /giropops # Qual o endpoint que vamos utilizar para se conectar ao container - alterado para dar erro
            port: 80 # Qual porta TCP vamos utilizar para se conectar ao container
          initialDelaySeconds: 10 # Quantos segundos vamos esperar para executar a primeira verificação
          periodSeconds: 10 # A cada quantos segundos vamos executar a verificação
          timeoutSeconds: 5 # Quantos segundos vamos esperar para considerar que a verificação falhou
          failureThreshold: 3 # Quantos falhas consecutivas vamos aceitar antes de reiniciar o container
```

**Comandos**

```bash
kubectl apply -f deployment.yaml

kubeclt get pods

kubectl describe pod nginx-deployment-<hs-do-pod>
```

**Explicação**
Você pode ver que o Kubernetes está tentando executar a nossa `livenessProbe` e ela está falhando, inclusive ele mostra a quantidade de vezes que ele tentou executar a `livenessProbe` e falhou, e com isso, ele reiniciou o nosso `Pod`
- afinal o nosso `endpoint` está errado.

#### Documentação
- [Kubernetes Documentation - Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Livro: Descomplicando o Kubernetes - Day 4](https://github.com/badtuxx/DescomplicandoKubernetes/blob/main/pt/day-4/README.md#liveness-probe)


## 9 - Readiness Probe

É uma forma de o Kubernetes verificar se o container está pronto para receber tráfego, ou seja, **se ele está pronto para receber requisições vindas de fora**.
- Verificar se o serviço está pronto para receber requisições

Essa é a nossa probe de leitura, ela fica verificando se o nosso container está pronto para receber requisições, e se estiver pronto, ele irá receber requisições, caso contrário, ele não irá receber requisições, pois será removido do `endpoint` do serviço, fazendo com que o tráfego não chegue até ele.
- são executadas no container durante todo o seu ciclo de vida;
- se falhar, vai remover o pod do endepoint.

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          exec:
            command:
              - curl
              - -f
              - http://localhost:80/
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
          successThreshold: 1
```

### readiness HTTP request

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        readinessProbe: # Onde definimos a nossa probe de leitura
          httpGet: # O tipo de teste que iremos executar, neste caso, iremos executar um teste HTTP
            path: / # O caminho que iremos testar
            port: 80 # A porta que iremos testar
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          periodSeconds: 10 # De quanto em quanto tempo iremos executar a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 2 # O número de vezes que a probe precisa passar para considerar que o container está pronto
          failureThreshold: 3 # O número de vezes que a probe precisa falhar para considerar que o container não está pronto
```

**Comandos**

```bash
kubectl apply -f nginx-deployment.yaml

kubectl get pods

kubectl describe pod nginx-deployment-<>
```

### Teste de falha

```yaml
...
        readinessProbe: # Onde definimos a nossa probe de leitura
          httpGet: # O tipo de teste que iremos executar, neste caso, iremos executar um teste HTTP
            path: /giropops # O caminho que iremos testar
            port: 80 # A porta que iremos testar
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          periodSeconds: 10 # De quanto em quanto tempo iremos executar a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 2 # O número de vezes que a probe precisa passar para considerar que o container está pronto
          failureThreshold: 3 # O número de vezes que a probe precisa falhar para considerar que o container não está pronto
```

**Comandos**

```bash
kubectl apply -f nginx-deployment.yaml

deployment.apps/nginx-deployment configured

kubectl get pods

## Ver o rollout
kubectl rollout status deployment/nginx-deployment

## Detalhe do pod que está com problemas
kubectl describe pod nginx-deployment-<>
```

**Explicação do erro**
- o nosso `rollout` não terminou, ele continua esperando a nossa probe passar
- o nosso `Pod` não está saudável, e por isso o Kubernetes não está conseguindo atualizar o nosso `Deployment`.

💡 *A **readiness probe** e a **liveness probe** não dependem uma da outra para serem bem-sucedidas. Se quiser esperar antes de executar uma **readiness probe**, você deve usar `InitialDelaySeconds` ou **startup probe**.*

## 10 - StartUp Probe

É a probe responsável por verificar se o nosso container foi inicializado corretamente, e se ele está pronto para receber requisições.
- Faz o healthcheck quando o Pod / container sobe

É parecida com a `readinessProbe`, mas a diferença é que a `startupProbe` é executada **apenas uma vez** no começo da vida do nosso container, e a `readinessProbe` é executada de tempos em tempos.

Criar o arquivo `nginx-startup.yaml`:

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        startupProbe: # Onde definimos a nossa probe de inicialização
          httpGet: # O tipo de teste que iremos executar, neste caso, iremos executar um teste HTTP
            path: / # O caminho que iremos testar
            port: 80 # A porta que iremos testar
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 2 # O número de vezes que a probe precisa passar para considerar que o container está pronto
```

**Comandos**
```bash
`kubectl apply -f nginx-startup.yaml`
```

### Entendendo a falha

- a `successThreshold` não pode ser maior que 1, pois a `startupProbe` é executada apenas uma vez,
- `failureThreshold` não pode ser maior que 1
- Usar o comando `kubectl describe` para ver qual probe está falhando
    - Vai estar no status `CrashLoopbackOff`

```yaml
...
        startupProbe: # Onde definimos a nossa probe de inicialização
          httpGet: # O tipo de teste que iremos executar, neste caso, iremos executar um teste HTTP
            path: / # O caminho que iremos testar
            port: 80 # A porta que iremos testar
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          periodSeconds: 10 # De quanto em quanto tempo iremos executar a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 2 # O número de vezes que a probe precisa passar para considerar que o container está pronto
          failureThreshold: 3 # O número de vezes que a probe precisa falhar para considerar que o container não está pronto
```

**Comandos**

```bash
kubectl apply -f nginx-startup.yaml

kubectl get pods

kubectl describe pod nginx-deployment-<identificacao-do-pod>
```

## 11 - Exemplo com todas as probes

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
      - image: nginx:1.19.2
        name: nginx
        resources:
          limits:
            cpu: "0.5"
            memory: 256Mi
          requests:
            cpu: 0.25
            memory: 128Mi
        livenessProbe: # Onde definimos a nossa probe de vida
          exec: # O tipo exec é utilizado quando queremos executar algo dentro do container.
            command: # Onde iremos definir qual comando iremos executar
              - curl
              - -f
              - http://localhost:80/
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          periodSeconds: 10 # De quanto em quanto tempo iremos executar a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 1 # O número de vezes que a probe precisa passar para considerar que o container está pronto
          failureThreshold: 3 # O número de vezes que a probe precisa falhar para considerar que o container não está pronto
        readinessProbe: # Onde definimos a nossa probe de prontidão
          httpGet: # O tipo de teste que iremos executar, neste caso, iremos executar um teste HTTP
            path: / # O caminho que iremos testar
            port: 80 # A porta que iremos testar
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          periodSeconds: 10 # De quanto em quanto tempo iremos executar a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 1 # O número de vezes que a probe precisa passar para considerar que o container está pronto
          failureThreshold: 3 # O número de vezes que a probe precisa falhar para considerar que o container não está pronto
        startupProbe: # Onde definimos a nossa probe de inicialização
          tcpSocket: # O tipo de teste que iremos executar, neste caso, iremos executar um teste TCP
            port: 80 # A porta que iremos testar
          initialDelaySeconds: 10 # O tempo que iremos esperar para executar a primeira vez a probe
          timeoutSeconds: 5 # O tempo que iremos esperar para considerar que a probe falhou
          successThreshold: 1 # O número de vezes que a probe precisa passar para considerar que o container está pronto
```

## Desafio Day 4

Criar 03 manifestos diferentes de Deployment com os seguintes itens:

- Limite de recursos
- Strategy
- Probes configuradas

### Manifesto 1

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: webapp-nginx-desafio1
  name: webapp-nginx-desafio1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp-nginx-desafio1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: webapp-nginx-desafio1
    spec:
      containers:
      - name: webapp-nginx
        image: nginx:1.28.0-alpine
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        resources:
          limits:
            memory: 128Mi
            cpu: 0.5
          requests:
            memory: 64Mi
            cpu: 0.3
        startupProbe:
          tcpSocket:
            port: 80
          initialDelaySeconds: 5
          timeoutSeconds: 5
          successThreshold: 1
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 10
          successThreshold: 1
          failureThreshold: 3
```

### Manifesto 2

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: app-apache-desafio2
  name: app-apache-desafio2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-apache-desafio2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: app-apache-desafio2
    spec:
      containers:
      - image: httpd:2.4-alpine
        name: app-apache
        resources:
          limits:
            memory: 256Mi
            cpu: 0.5
          requests:
            memory: 128Mi
            cpu: 0.25
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        livenessProbe:
          tcpSocket:
            port: 80
          initialDelaySeconds: 5
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
```

### Manifesto 3

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-debian-desafio3
  labels:
    app: app-debian-desafio3
spec:
  replicas: 4
  selector:
    matchLabels:
      app: app-debian-desafio3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: app-debian-desafio3
    spec:
      containers:
      - name: app-debian
        image: debian:bullseye-slim
        command: ["sh", "-c", "sleep 600"]
        resources:
          limits:
            memory: "256Mi"
            cpu: "500m"
          requests:
            memory: "128Mi"
            cpu: "300m"
        startupProbe:
          exec:
            command: ["sh", "-c", "echo 'Startup probe: OK'"]
          initialDelaySeconds: 5
          periodSeconds: 10
          successThreshold: 1
        livenessProbe:
          exec:
            command: ["sh", "-c", "echo 'Liveness probe: OK'"]
          initialDelaySeconds: 10
          timeoutSeconds: 10
          successThreshold: 1
          failureThreshold: 3
        readinessProbe:
          exec:
            command: ["sh", "-c", "echo 'Readiness probe: OK'"]
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
```