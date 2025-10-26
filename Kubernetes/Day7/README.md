# Índice - Day 7

## 1 - O que é um StatefulSet

O StatefulSet é um recurso do Kubernetes responsável por gerenciar o deployment e o scaling de Pods que exigem identidade e persistência.

Diferente de Deployments e ReplicaSets, que são voltados para aplicações *stateless* (sem estado), o StatefulSet é usado quando é necessário garantir nomes, endereços e a ordem de criação e exclusão dos Pods de forma consistente e estável ao longo do tempo.

Os StatefulSets são indicados para aplicações que exigem uma ou mais das seguintes características:
- Identidade de rede estável e única;
- Armazenamento persistente e consistente;
- Controle sobre a sequência de criação e dimensionamento dos Pods;
- Garantia de ordem durante atualizações e reversões (rolling updates e rollbacks);
- Esses requisitos são comuns em aplicações como bancos de dados, sistemas de mensageria (filas) e outras aplicações que dependem de persistência de dados ou de uma identidade de rede previsível.
  
**Principais características**:
- **StatefulSet** cria Pods replicados com identidade única (índice e hostname fixos);
- Diferente de **Deployments/ReplicaSets**, os Pods não são intercambiáveis;
- Os Pods são criados e atualizados em ordem garantida (ex: giropops-0 antes de giropops-1);
  - se um StatefulSet tiver um nome giropops e um spec com três réplicas, ele criará três Pods: giropops-0, giropops-1, giropops-2.
- Integra-se com **Volumes Persistentes (PV)**, garantindo que cada Pod mantenha seus dados ao ser recriado.
- Cada Pod recebe seu próprio PV, útil para aplicações com necessidade de dados persistentes, como bancos de dados.

#### StatefulSet e Headless Service
**Headless Service**: tipo de serviço sem IP próprio, retorna diretamente os IPs dos Pods.
- Em conjunto com o **StatefulSet**, fornece nomes DNS estáveis para cada Pod.
- Cada Pod recebe um hostname no formato:
   `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.
- Isso permite que os Pods sejam acessados individualmente e com identidade de rede fixa.
- Essencial para aplicações **stateful** (como bancos de dados), onde cada instância precisa de um endereço previsível para comunicação.

**Exemplo**

Imagine que temos um StatefulSet chamado giropops com três réplicas e um Headless Service denominado nginx, os Pods gerados serão giropops-0, giropops-1 e giropops-2. Cada um deles receberá um endereço DNS exclusivo, respectivamente: `giropops-0.nginx.default.svc.cluster.local`, `giropops-1.nginx.default.svc.cluster.local` e `giropops-2.nginx.default.svc.cluster.local`.

#### Documentação
- [Kubernetes Doc - StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Livro Descomplicando Kubernetes - Day 7](https://livro.descomplicandokubernetes.com.br/pt/day-7/)

## 2 - Criando o nosso primeiro StatefulSet

No exemplo, o StatefulSet gerencia o Nginx, dando a cada Pod um volume persistente (PV) e uma página web exclusiva.
- Vamos criar o arquivo `statefulset-nginx.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nginx
spec:
  serviceName: "nginx"
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21.0
        ports:
        - containerPort: 80
          name: http
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

**Comandos**

```bash
## Apply
kubectl apply -f nginx-statefulset.yaml

## Verificar se o StatefulSet foi criado
kubectl get statefulset

## Ver mais detalhes
kubectl describe statefulset nginx

## Verificar se os pods foram criados
kubectl get pods
```

## 3 - Criando o nosso Headless Service

- Vamos criar o arquivo `nginx-headless-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: http
  clusterIP: None # Como estamos criando um Headless Service, não queremos que ele tenha um IP, então definimos o clusterIP como None
  selector:
    app: nginx
```

**Comandos**

```bash
kubectl apply -f nginx-headless-service.yaml

## Verificar se foi criado
kubectl get service

## Ver com mais detalhes
kubectl describe service nginx

## Acessar um pod - nginx-0
kubectl exec -ti nginx-0 -- bash
>> cd /usr/share/nginx/html
>> curl localhost
>> echo "Gripops-0" > index.html

## Acessar outro pod - nginx-1
kubectl exec -ti nginx-1 -- bash
>> curl nginx-0.nginx.default.svc.cluster.local
```

#### Documentação
- [Kubernetes Doc - Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)

## 4 - Removendo o nosso StatefulSet

**Comandos**

```bash
## Excluindo um StatefulSet
kubectl delete statefulset nginx

## Outra forma de excluir
kubectl delete -f nginx-statefulset.yaml

## Excluindo um Headless Service
kubectl delete service nginx

kubectl delete -f nginx-headless-service.yaml

## Excluindo um PVC
kubectl delete pvc www-0
```

## 5 - O que são Services

São uma abstração que expõe Pods de forma estável, independente de onde estão no cluster.

**Tipos principais de Services**:
- **ClusterIP**: acesso interno no cluster (padrão) - cria um IP local para esse acesso interno. Este tipo torna o Service acessível apenas dentro do cluster.
- **NodePort**: acesso externo via `<NodeIP>:<NodePort>` - usa o NAT. Torna o Service acessível de fora do cluster.
- **LoadBalancer**: cria um balanceador de carga externo (se suportado pela nuvem), e atribui um IP fixo, externo ao cluster, ao Service.
- **ExternalName**: Mapeia o Service para o conteúdo do campo externalName (por exemplo, [foo.bar.example.com](http://foo.bar.example.com/)), retornando um registro CNAME com seu valor.

**Funcionamento**:
- Usa **labels** para selecionar Pods.
- Mantém **IP e porta estáveis**, mesmo com troca de Pods.
- Cria automaticamente **Endpoints**, que rastreiam IPs e portas dos Pods associados.

```bash
## Ver o endpoints
kubectl get endpoints meu-service
```

#### Documentação
    - https://kubernetes.io/docs/concepts/services-networking/service/

## 6 - Criando os nossos Services ClusterIP e NodePort

- Criando o Deployment e fazendo o expose

```bash
## Criar um deployment
kubectl create deployment nginx --image nginx:1.20.1 --port 80

## Fazer o expose
kubectl expose deployment nginx
```

Saída:

```
NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1      <none>        443/TCP   41d
nginx        ClusterIP   10.96.171.74   <none>        80/TCP    1s
```

**Continuando**

```bash
## Fazer o expose
kubectl expose deployment nginx --type NodePort

## Outra forma
kubectl expose deployment meu-deployment --type=NodePort --port=80 --target-port=8080
```

Saida:

```bash
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP        41d
nginx        NodePort    10.96.112.186   <none>        80:30571/TCP   7s
```

**Visualizar os Services e Endpoints**

```bash
## Ver os svc
kubectl get services

## Descrever
kubectl describe svc nginx

## Listar os endpoinst
kubectl get endpoints

## Escalar e listar endpoins
kubectl scale deployment nginx --replicas 3
kubectl get endpoints
```
## 7 - Criando os nosso Services Load Balancer e ExernalName

O Service do tipo LoadBalancer é uma das formas mais comuns de expor um serviço ao tráfego da internet no Kubernetes. Ele provisiona automaticamente um balanceador de carga do provedor de nuvem onde seu cluster Kubernetes está rodando, se houver algum disponível.

```bash
## Criar o deployment 
kubectl create deployment nginx --image nginx:1.20.1 --port 80 --replicas 3

## Criar um svc do tipo 
kubectl expose deployment nginx --type=LoadBalancer --port=80 --target-port=8080

## Ver os services
kubectl get services
```

- Criar via manifesto YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: meu-service
spec:
  type: LoadBalancer
  selector:
    app: meu-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

Esse tipo de serviço é recomendado em situações como:

- **Provedores de nuvem**: Quando o Kubernetes está hospedado em plataformas que oferecem suporte nativo a balanceadores de carga, como AWS, GCP ou Azure. Ao criar um serviço do tipo LoadBalancer, o balanceador é automaticamente provisionado pelo provedor.

- **Exposição externa da aplicação**: Quando há necessidade de acesso à aplicação fora do cluster. Nesse caso, o LoadBalancer disponibiliza um endereço IP público que direciona o tráfego externo para os Pods correspondentes.

## 8 - ExternalName

O ExternalName não expõe um conjunto de `Pods`, mas sim um nome de host externo. Pode ser, por exemplo, um serviço que expõe um banco de dados externo, ou um serviço que expõe um serviço de e-mail externo.

O tipo `ExternalName` é útil quando queremos:

- **Criação de um alias para um serviço externo**: Imagine que você possua um banco de dados hospedado fora do cluster Kubernetes, mas deseja que as aplicações internas o acessem usando um nome interno, como se fosse um serviço do próprio cluster. Nesse caso, o ExternalName permite mapear um alias para o endereço externo do banco de dados.

- **Abstração de serviços por ambiente**: Também é útil quando existem diferentes ambientes, como produção e desenvolvimento, que utilizam serviços externos distintos. Assim, é possível manter o mesmo nome de serviço em todos os ambientes, alterando apenas o endereço de destino conforme o contexto.

```bash
kubectl create service externalname giropops-db --external-name meu-db.giropops.com.br
```

- Criar via manifesto YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: meu-service
spec:
  type: ExternalName
  externalName: meu-db.giropops.com.br
```

**Comandos**

```bash
## Ver os services
kubectl get services

## Listar os svc de uma namespace específica
kubectl get services -n kube-system

## Visualizar os services de todasa as namespaces
kubectl get services -A

## Ver detalhes de um service específico
kubectl describe service meu-service
```

## 9 - Criando o Service expondo outro Service


```bash
kubectl expose service --name giropops nginx --type NodePort
```

## 10 - Criando os Services através de YAML

Criando o Deployment Nginx

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        env: dev
    spec:
      containers:
      - name: nginx
        image: nginx:1.21.0
        ports:
        - containerPort: 80
          name: http
          protocol: TCP

```

- ClusterIP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
    env: dev
spec:
  selector:
    app: nginx
  ports:
   - port: 80
     name: http
     targetPort: 80
  type: ClusterIP
```

- NodePort

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
  labels:
    app: nginx
    env: dev
spec:
  selector:
    app: nginx
  ports:
   - port: 80  # Porta do Service, que será mapeada para a porta 80 do Pod
     name: http
     targetPort: 80 # Porta dos Pods
     nodePort: 32000 # Porta do Node, que será mapeada para a porta 80 do Service
  type: NodePort
```

- LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-loadbalancer
  labels:
    app: nginx
    env: dev
spec:
  selector:
    app: nginx
  ports:
   - port: 80
     name: http
     targetPort: 80
  type: LoadBalancer
```

- EternalName

```yaml
apiVersion: v1
kind: Service
metadata:
  name: meu-service
spec:
  type: ExternalName
  externalName: meu-db.giropops.com.br
```

- Saídas

```bash
NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
kubernetes           ClusterIP      10.96.0.1       <none>        443/TCP        4m33s
nginx                ClusterIP      10.96.72.6      <none>        80/TCP         4m29s
nginx-loadbalancer   LoadBalancer   10.96.126.147   <pending>     80:32098/TCP   5s
nginx-nodeport       NodePort       10.96.116.137   <none>        80:32000/TCP   2m6s
```

## Lição de casa Day-7

1- Criação e gerenciamento de StatefulSet
- Crie um StatefulSet simples com dois Pods.
- Escale o StatefulSet para mais réplicas.
- Exclua um Pod e observe como o Kubernetes o recria automaticamente.

2- Trabalhando com Services
- Exponha o StatefulSet usando um Service do tipo ClusterIP.
- Altere o tipo para NodePort ou LoadBalancer e teste o acesso à aplicação.
- Verifique a conectividade entre os Pods e o serviço exposto.

3- Criando um Service ExternalName
- Crie um Service do tipo ExternalName apontando para um serviço externo (à sua escolha).
- Teste o acesso ao serviço externo a partir de dentro dos Pods.