# Índice - Day 10

## 1 - O que é um ServiceMonitor

O ServiceMonitor é um recurso do Prometheus Operator que define como o Prometheus deve coletar métricas de um serviço.
- Cada serviço que você deseja monitorar precisa ter seu próprio ServiceMonitor configurado.
- Ele especifica detalhes como endpoints, porta, caminho e também permite adicionar rótulos personalizados.
- É possível aplicar filtros para selecionar apenas determinados pods, como por exemplo aqueles com o rótulo `app=nginx`.

O Kube-Prometheus já inclui diversos ServiceMonitors prontos, como os do API Server, Node Exporter e Blackbox Exporter.

```bash
## Verificar o conteúdo de um ServiceMonitor
kubectl get servicemonitor prometheus-k8s -n monitoring -o yaml
```

- Arquivo yaml

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  annotations:
  labels:
    app.kubernetes.io/component: prometheus
    app.kubernetes.io/instance: k8s
    app.kubernetes.io/name: prometheus
    app.kubernetes.io/part-of: kube-prometheus
    app.kubernetes.io/version: 2.41.0
  name: prometheus-k8s
  namespace: monitoring
spec:
  endpoints:
  - interval: 30s
    port: web
  - interval: 30s
    port: reloader-web
  selector:
    matchLabels:
      app.kubernetes.io/component: prometheus
      app.kubernetes.io/instance: k8s
      app.kubernetes.io/name: prometheus
      app.kubernetes.io/part-of: kube-prometheus
```

## 2 - Criando o nosso Deployment e Service no K8s

Cenário:
- vamos criar uma aplicação com Nginx e utilizar o exporter do Nginx para monitorarmos o nosso serviço;
- vamos criar um outro pod para que possamos criar um teste de carga para a nossa aplicação, realizando assim uma carga de até 1000 requisições por segundo.

#### **Passos**

1. **Criar um ConfigMap onde terá a configuração que queremos para o nosso Nginx.**

```yaml
apiVersion: v1 # versão da API
kind: ConfigMap # tipo de recurso, no caso, um ConfigMap
metadata: # metadados do recurso
  name: nginx-config # nome do recurso
data: # dados do recurso
  nginx.conf: | # inicio da definição do arquivo de configuração do Nginx
    server {
      listen 80;
      location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
      }
      location /metrics {
        stub_status on;
        access_log off;
      }
    }
```

**Onde**:

- `apiVersion`: Versão da API do Kubernetes que estamos utilizando.
- `kind`: Tipo de objeto que estamos criando.
- `metadata`: Informações sobre o objeto que estamos criando.
- `metadata.name`: Nome do nosso objeto.
- `data`: Dados que serão utilizados no nosso ConfigMap.
- `data.nginx.conf`: A configuração do Nginx.

**Comandos**

```bash
kubectl apply -f nginx-config.yaml

kubectl get configmaps
```

2. **Criar a aplicação**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: nginx-server
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 3
  template:
    metadata:
       labels:
         app: nginx
       annotations: # annotations do template
         prometheus.io/scrape: "true" # habilita o scraping do Prometheus
         prometheus.io/port: "9113" # porta do target
    spec:
      containers:
      - name: nginx
        image: nginx:1.21.1
        ports:
        - containerPort: 80
          name: http
        volumeMounts: # volumes que serão montados no container
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: nginx.conf
      - name: nginx-exporter # nome do container que será o exporter
        image: 'nginx/nginx-prometheus-exporter:1.1' # imagem do container do exporter
        args: # argumentos do container
          - '-nginx.scrape-uri=http://localhost/metrics' # argumento para definir a URI de scraping
        resources:
          limits:
            memory: 128Mi
            cpu: 0.3
        ports:
        - containerPort: 9113 # porta do container que será exposta
          name: metrics
    volumes:  # volumes do template
    - configMap: # configmap do volume, nós iremos criar esse volume através de um configmap
        dafaultMode: 420 # modo padrão do volume
        name: nginx-config # nome do configmap
      name: nginx-config  # nome do volume
```

**Onde**

- `apiVersion`: Versão da API do Kubernetes que estamos utilizando.
- `kind`: Tipo de objeto que estamos criando.
- `metadata`: Informações sobre o objeto que estamos criando.
- `metadata.name`: Nome do nosso objeto.
- `spec`: Especificações do nosso objeto.
- `spec.selector`: Selector que o ServiceMonitor irá utilizar para encontrar os serviços que ele irá monitorar.
- `spec.selector.matchLabels`: Labels que o ServiceMonitor irá utilizar para encontrar os serviços que ele irá monitorar.
- `spec.selector.matchLabels.app`: Label que o ServiceMonitor irá utilizar para encontrar os serviços que ele irá monitorar.
- `spec.replicas`: Quantidade de réplicas que o nosso Deployment irá criar.
- `spec.template`: Template que o nosso Deployment irá utilizar para criar os pods.
- `spec.template.metadata`: Informações sobre o nosso pod.
- `spec.template.metadata.labels`: Labels que serão adicionadas ao nosso pod.
- `spec.template.metadata.labels.app`: Label que será adicionada ao nosso pod.
- `spec.template.metadata.annotations`: Annotations que serão adicionadas ao nosso pod.
- `spec.template.metadata.annotations.prometheus.io/scrape`: Annotation que será adicionada ao nosso pod.
- `spec.template.metadata.annotations.prometheus.io/port`: Annotation que será adicionada ao nosso pod.
- `spec.template.spec`: Especificações do nosso pod.
- `spec.template.spec.containers`: Containers que serão criados no nosso pod.
- `spec.template.spec.containers.name`: Nome do nosso container.
- `spec.template.spec.containers.image`: Imagem que será utilizada no nosso container.
- `spec.template.spec.containers.ports`: Portas que serão expostas no nosso container.
- `spec.template.spec.containers.ports.containerPort`: Porta que será exposta no nosso container.
- `spec.template.spec.containers.volumeMounts`: Volumes que serão montados no nosso container.
- `spec.template.spec.containers.volumeMounts.name`: Nome do volume que será montado no nosso container.
- `spec.template.spec.containers.volumeMounts.mountPath`: Caminho que o volume será montado no nosso container.
- `spec.template.spec.containers.volumeMounts.subPath.nginx.conf`: Subpath que o volume será montado no nosso container.
- `spec.template.spec.volumes`: Volumes que serão criados no nosso pod.
- `spec.template.spec.volumes.configMap`: ConfigMap que será utilizado no nosso volume.
- `spec.template.spec.volumes.configMap.defaultMode`: Modo de permissão que o volume será criado.
- `spec.template.spec.volumes.configMap.name`: Nome do ConfigMap que será utilizado no nosso volume.
- `spec.template.spec.volumes.name`: Nome do nosso volume.

**Comandos**

```bash
## Criar o deployment
kubectl apply -f nginx-deployment.yaml

## Verificar o pod
kubectl get pods

## Verificar o deployment
kubectl get deployments
```

3. **Criar um Service**

```yaml
apiVersion: v1 # versão da API
kind: Service # tipo de recurso, no caso, um Service
metadata: # metadados do recurso
  name: nginx-svc # nome do recurso
  labels: # labels do recurso
    app: nginx # label para identificar o svc
spec: # especificação do recurso
  ports: # definição da porta do svc 
  - port: 9113 # porta do svc
    name: metrics # nome da porta
  selector: # seletor para identificar os pods/deployment que esse svc irá expor
    app: nginx # label que identifica o pod/deployment que será exposto
```

**Onde**:

- `apiVersion`: Versão da API do Kubernetes que estamos utilizando.
- `kind`: Tipo de objeto que estamos criando.
- `metadata`: Informações sobre o objeto que estamos criando.
- `metadata.name`: Nome do nosso objeto.
- `spec`: Especificações do nosso objeto.
- `spec.selector`: Selector que o Service irá utilizar para encontrar os pods que ele irá expor.
- `spec.selector.app`: Label que o Service irá utilizar para encontrar os pods que ele irá expor.
- `spec.ports`: Configurações das portas que serão expostas no nosso Service.
- `spec.ports.protocol`: Protocolo que será utilizado na porta que será exposta.
- `spec.ports.port`: Porta que será exposta no nosso Service.
- `spec.ports.name`: Nome da porta que será exposta no nosso Service.

**Comandos**

```bash
## Criar o service
kubectl apply -f nginx-service.yaml

## Verificar se foi criado
kubectl get services

## Acessr o pod
kubectl exec -it pod nginx-server-79f57847b7-84c9s -- bash
 > curl localhost/metrics
 > curl localhost:9113/metrics

## Verificar e o Nginx está rodando
curl http://<EXTERNAL-IP-DO-SERVICE>:80

## Verificar se as métricas do Nginx estão sendo expostas 
curl http://<EXTERNAL-IP-DO-SERVICE>:80/nginx_status

## Verificar se as métricas do Nginx Exporter estão sendo expostas
curl http://<EXTERNAL-IP-DO-SERVICE>:80/metrics
```

## 3 - Criando um ServiceMonitor

- Criar o ServiceMonitor com o arquivo YAML

```yaml
apiVersion: monitoring.coreos.com/v1 # versão da API
kind: ServiceMonitor # tipo de recurso, no caso, um ServiceMonitor do Prometheus Operator
metadata: # metadados do recurso
  name: nginx-servicemonitor # nome do recurso
  labels: # labels do recurso
    app: nginx # label que identifica o app
spec: # especificação do recurso
  selector: # seletor para identificar os pods que serão monitorados
    matchLabels: # labels que identificam os pods que serão monitorados
      app: nginx # label que identifica o app que será monitorado
  endpoints: # endpoints que serão monitorados
    - interval: 10s # intervalo de tempo entre as requisições
      path: /metrics # caminho para a requisição
      targetPort: 9113 # porta do target
```

**Onde**

- `apiVersion`: Versão da API do Kubernetes que estamos utilizando.
- `kind`: Tipo de objeto que estamos criando, no nosso caso, um ServiceMonitor.
- `metadata`: Informações sobre o objeto que estamos criando.
- `metadata.name`: Nome do nosso objeto.
- `metadata.labels`: Labels que serão utilizadas para identificar o nosso objeto.
- `spec`: Especificações do nosso objeto.
- `spec.selector`: Seletor que será utilizado para identificar o nosso Service.
- `spec.selector.matchLabels`: Labels que serão utilizadas para identificar o nosso Service, no nosso caso, o Service que tem a label `app: nginx`.
- `spec.endpoints`: Endpoints que serão monitorados pelo Prometheus.
- `spec.endpoints.interval`: Intervalo de tempo que o Prometheus irá capturar as métricas, no nosso caso, 15 segundos.
- `spec.endpoints.path`: Caminho que o Prometheus irá fazer a requisição para capturar as métricas, no nosso caso, `/metrics`.
- `spec.endpoints.targetPort`: Porta que o Prometheus irá fazer a requisição para capturar as métricas, no nosso caso, `9113`.

**Comandos**

```bash
## Criar o ServiceMonitor
kubectl apply -f nginx-service-monitor.yaml

## Ver se o ServiceMonitor está rodando
kubectl get servicemonitors

## Fazer o port-forward do Prometheus
kubectl port-forward -n monitoring svc/prometheus-k8s 39090:9090

## Verificar se o Prometheus está capturando as métricas do Nginx e do Nginx Exporter
curl http://localhost:39090/api/v1/targets
```

## 4 - Criando um novo pod e o nosso PodMonitor

Em alguns casos, não existe um Service na frente dos Pods, como em CronJobs, Jobs ou DaemonSets.Nessas situações, utiliza-se o *PodMonitor* para coletar métricas diretamente dos Pods. Esse recurso é útil, por exemplo, para monitorar pods não HTTP, como aqueles que expõem métricas de RabbitMQ, Redis ou Kafka.

- Vamos criar um Pod com o arquivo `nginx-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata: 
  name: nginx-pod
  labels:
	  app: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx:1.21.1
      ports:
      - containerPort: 80
        name: http
      volumeMounts: # volumes que serão montados no container
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: nginx.conf
    - name: nginx-exporter # nome do container que será o exporter
      image: 'nginx/nginx-prometheus-exporter:1.1' # imagem do container do exporter
      args: # argumentos do container
        - '-nginx.scrape-uri=http://localhost/metrics' # argumento para definir a URI de scraping
      resources:
        limits:
          memory: 128Mi
          cpu: 0.3
      ports:
      - containerPort: 9113 # porta do container que será exposta
        name: metrics
  volumes:  # volumes do template
  - configMap: # configmap do volume, nós iremos criar esse volume através de um configmap
     defaultMode: 420 # modo padrão do volume
     name: nginx-config # nome do configmap
    name: nginx-config  # nome do volume
```

- Vamos criar o nosso PodMonitor com o seguinte arquivo YAML chamado `nginx-pod-monitor.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1 # versão da API
kind: PodMonitor # tipo de recurso, no caso, um PodMonitor do Prometheus Operator
metadata: # metadados do recurso
  name: nginx-podmonitor # nome do recurso
  labels: # labels do recurso
    app: nginx-pod # label que identifica o app
spec:
  namespaceSelector: # seletor de namespaces
    matchNames: # namespaces que serão monitorados
      - default # namespace que será monitorado
  selector: # seletor para identificar os pods que serão monitorados
    matchLabels: # labels que identificam os pods que serão monitorados
      app: nginx # label que identifica o app que será monitorado
  podMetricsEndpoints: # endpoints que serão monitorados
    - interval: 10s # intervalo de tempo entre as requisições
      path: /metrics # caminho para a requisição
      targetPort: 9113 # porta do target
```

**Onde**:

- usamos o `podMetricsEndpoints` para definir os endpoints que serão monitorados
- o `namespaceSelector` é utilizado para selecionar os namespaces que serão monitorados

**Criar o Pod do Nginx**

- Com o arquivo YAML chamado `nginx-pod.yaml`

```yaml
apiVersion: v1 # versão da API
kind: Pod # tipo de recurso, no caso, um Pod
metadata: # metadados do recurso
  name: nginx-pod # nome do recurso
  labels: # labels do recurso
    app: nginx # label que identifica o app
spec: # especificações do recursos
  containers: # containers do template 
    - name: nginx-container # nome do container
      image: nginx # imagem do container do Nginx
      ports: # portas do container
        - containerPort: 80 # porta do container
          name: http # nome da porta
      volumeMounts: # volumes que serão montados no container
        - name: nginx-config # nome do volume
          mountPath: /etc/nginx/conf.d/default.conf # caminho de montagem do volume
          subPath: nginx.conf # subpath do volume
    - name: nginx-exporter # nome do container que será o exporter
      image: 'nginx/nginx-prometheus-exporter:0.11.0' # imagem do container do exporter
      args: # argumentos do container
        - '-nginx.scrape-uri=http://localhost/metrics' # argumento para definir a URI de scraping
      resources: # recursos do container
        limits: # limites de recursos
          memory: 128Mi # limite de memória
          cpu: 0.3 # limite de CPU
      ports: # portas do container
        - containerPort: 9113 # porta do container que será exposta
          name: metrics # nome da porta
  volumes: # volumes do template
    - configMap: # configmap do volume, nós iremos criar esse volume através de um configmap
        defaultMode: 420 # modo padrão do volume
        name: nginx-config # nome do configmap
      name: nginx-config # nome do volume
```

**Comandos**

```bash
## Criar o pod
kubectl apply -f nginx-pod.yaml

## Criar o podmonitor
kubectl apply -f nginx-pod-monitor.yaml

## Verificar os podmonitors
kubectl get podmonitors

kubectl get podmonitors.monitoring.coreos.com

## Ver os detalhes
kubectl describe podmonitors nginx-podmonitor

## Ver os detalhes do servicemonitor
kubectl describe servicemonitors nginx-servicemonitor

## Ver se ele está aparecendo como um target no Prometheus
kubectl port-forward -n monitoring svc/prometheus-k8s 39090:9090

## Acessar o container e verificar se o exporter está funcionando corretamente
kubectl exec -it nginx-pod -c nginx-exporter -- bash
> curl localhost:9113/metrics

```

## 5 - Criando alertas no Prometheus e Alertmanager através do Prometheus Rule

- Configurar o Prometheus para monitorar o nosso cluster. Para isso, vamos utilizar o `kubectl port-forward` para acessar o Prometheus localmente:

```bash
## Port foward
kubectl port-forward -n monitoring svc/prometheus-k8s 39090:9090

## Se quiser acessar o Alertmanager, basta executar o seguinte comando:
kubectl port-forward -n monitoring svc/alertmanager-main 39093:9093
```

Acessar o Prometheus e o AlertManager através do seu navegador,
- Prometheus: `http://localhost:39090`
- AlertManager: `http://localhost:39093`

**Comandos**

```bash
## Listar os configmaps do cluster
kubectl get configmaps -n monitoring

## Visualizar o conteúdo do configmap
kubectl get configmap prometheus-k8s-rulefiles-0 -n monitoring -o yaml
```

### Criando um novo alerta

O **PrometheusRule** é um recurso do Kubernetes que foi instalado no momento que realizamos a instalação dos CRDs do kube-prometheus. O PrometheusRule permite que você defina alertas para o Prometheus.
- Vamos criar um alerta para cuidar do Nginx

Para isso, vamos criar o arquivo `nginx-prometheus-rule.yaml`

```yaml
apiVersion: monitoring.coreos.com/v1 # Versão da api do PrometheusRule
kind: PrometheusRule # Tipo do recurso
metadata: # Metadados do recurso (nome, namespace, labels)
  name: nginx-prometheus-rule
  namespace: monitoring
  labels: # Labels do recurso
    prometheus: k8s # Label que indica que o PrometheusRule será utilizado pelo Prometheus do Kubernetes
    role: alert-rules # Label que indica que o PrometheusRule contém regras de alerta
    app.kubernetes.io/name: kube-prometheus # Label que indica que o PrometheusRule faz parte do kube-prometheus
    app.kubernetes.io/part-of: kube-prometheus # Label que indica que o PrometheusRule faz parte do kube-prometheus
spec: # Especificação do recurso
  groups: # Lista de grupos de regras
  - name: nginx-prometheus-rule # Nome do grupo de regras
    rules: # Lista de regras
    - alert: NginxDown # Nome do alerta
      expr: up{job="nginx"} == 0 # Expressão que será utilizada para disparar o alerta
      for: 1m # Tempo que a expressão deve ser verdadeira para que o alerta seja disparado
      labels: # Labels do alerta
        severity: critical # Label que indica a severidade do alerta
      annotations: # Anotações do alerta
        summary: "Nginx is down" # Título do alerta
        description: "Nginx is down for more than 1 minute. Pod name: {{ $labels.pod }}" # Descrição do alerta
```

**Comandos**

```bash
## Aplicar
kubectl apply -f nginx-prometheus-rule.yaml

## Verificar se foi criado
kubectl get prometheusrules -n monitoring
```

E olha o alerta aqui:
![Criando alerta](Criando%20alerta.png)

### **Cenário: mais um novo alerta**

Agora vamos criar um novo alerta para monitorar a quantidade de requisições simultâneas que o seu Nginx está recebendo, com uma nova regra no PrometheusRule.

```yaml
apiVersion: monitoring.coreos.com/v1 # Versão da api do PrometheusRule
kind: PrometheusRule # Tipo do recurso
metadata: # Metadados do recurso (nome, namespace, labels)
  name: nginx-prometheus-rule
  namespace: monitoring
  labels: # Labels do recurso
    prometheus: k8s # Label que indica que o PrometheusRule será utilizado pelo Prometheus do Kubernetes
    role: alert-rules # Label que indica que o PrometheusRule contém regras de alerta
    app.kubernetes.io/name: kube-prometheus # Label que indica que o PrometheusRule faz parte do kube-prometheus
    app.kubernetes.io/part-of: kube-prometheus # Label que indica que o PrometheusRule faz parte do kube-prometheus
spec: # Especificação do recurso
  groups: # Lista de grupos de regras
  - name: nginx-prometheus-rule # Nome do grupo de regras
    rules: # Lista de regras
    - alert: NginxDown # Nome do alerta
      expr: up{job="nginx"} == 0 # Expressão que será utilizada para disparar o alerta
      for: 1m # Tempo que a expressão deve ser verdadeira para que o alerta seja disparado
      labels: # Labels do alerta
        severity: critical # Label que indica a severidade do alerta
      annotations: # Anotações do alerta
        summary: "Nginx is down" # Título do alerta
        description: "Nginx is down for more than 1 minute. Pod name: {{ $labels.pod }}" # Descrição do alerta
    - alert: NginxHighRequestRate # Nome do alerta
      expr: rate(nginx_http_requests_total[5m]) > 10 # Expressão que será utilizada para disparar o alerta
      for: 1m # Tempo que a expressão deve ser verdadeira para que o alerta seja disparado
      labels: # Labels do alerta
        severity: warning # Label que indica a severidade do alerta
      annotations: # Anotações do alerta
        summary: "Nginx is receiving high request rate" # Título do alerta
        description: "Nginx is receiving high request rate for more than 1 minute. Pod name: {{ $labels.pod }}" # Descrição do alerta
```

**Comandos**

```bash
## Atualizar o PrometheusRule
kubectl apply -f nginx-prometheus-rule.yaml

## vVerificar se o PrometheusRule foi atualizado 
kubectl get prometheusrules -n monitoring nginx-prometheus-rule -o yaml
```

Com o novo alerta, caso o Nginx esteja recebendo mais de 10 requisições por minuto, o alerta será disparado e você receberá uma notificação.