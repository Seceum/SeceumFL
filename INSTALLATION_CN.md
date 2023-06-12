# 部署说明文档

欢迎使用SeceumFL开源联邦学习系统产品！！    
SeceumFL是[神谱科技](https://www.seceum.com/)在开源系统[FATE](https://github.com/FederatedAI)的基础上进行二次开发并做了优化后的联邦学习系统。    
其中包括子模块有：**FATE-Flow、FATE-Serving、FATE-Board、Eggroll**。    
在开始阶段，我们建议用两台物理机以及Docker来部署**SeceumFL**。    

SeceumFL会在每台机器上启动如下服务：

```shell
docker ps

CONTAINER ID      IMAGE                         COMMAND                  CREATED           STATUS      NAMES
7f0ce1b40acb      seceum-fl-web:3.2            "/docker-entrypoin..."   3 hours ago       Up 3 hours   seceum-web
38b09a6cf67d      seceum-fl:3.2                "/data/projects/py..."   6 hours ago       Up 3 hours   fate_flow_server
5ae51b0c3577      seceum-fl:3.2                "bash bin/serving_..."   26 hours ago      Up 26 hours  serving
3259f60efb28      seceum-fl:3.2                "/bin/bash"              5 hours ago       Up 5 hours   fateboard
ded5a9773602      seceum-fl:3.2                "./eggroll/bin/sta..."   26 hours ago      Up 4 hours   nodemanager
20b3b2d99406      seceum-fl:3.2                "./eggroll/bin/sta..."   26 hours ago      Up 4 hours   clustermanager
3c6d81d38202      seceum-fl:3.2                "./eggroll/bin/sta..."   26 hours ago      Up 4 hours   rollsite
8f64bfed233c      redis:6.0.8                 "docker-entrypoint..."   26 hours ago      Up 26 hours  redis
781af70bfb83      bitnami/zookeeper:latest    "/opt/bitnami/scri..."   26 hours ago      Up 26 hours  zookeeper
d41250c5676e      mysql:8.0.28                "docker-entrypoint..."   26 hours ago      Up 26 shours  mysql

```


## 1.    环境要求

| **操作系统** | CentOS 7.2                                                   |
| :----------- | :----------------------------------------------------------- |
| **工具依赖** | Docker, Docker-compose, Git, Python3.8 |
| **操作用户** | 用户组: Docker                                          |
| **系统配置** | 两台物理机，每一台最小配置8*Cores(核心）, 16G RAM |


## 2.    项目拉取

- 先从Github上拉取项目代码到服务器上如：/home/alice/
- 再从腾讯云上拉取SeceumFL的Docker镜像

```shell
cd /home/alice/
git clone https://github.com/Seceum/SeceumFL.git
docker pull ccr.ccs.tencentyun.com/seceum/seceum-fl:3.2
docker pull ccr.ccs.tencentyun.com/seceum/seceum-fl-web:3.2
```

将代码Clone（克隆）后，其目录结构如下（只摘取了重要的部分加以说明）：

```shell
tree -L 1 ./SeceumFL

SeceumFL
├── bin
├── build
├── c
├── Dockerfile
├── docker-compose.yml     --服务一键启动的docker compose配置文件
├── init_local_up.py       --简化配置过程的脚本，前提是已经配置好了eggroll里面的route_table.json
├── conf                   --服务的主要配置都在这里
├── eggroll                --eggroll服务依赖的代码和配置；该服务负责通讯、计算和数据存储
├── fateboard              --fateboard依赖的代码和配置；该服务查看任务状态
├── fate-serving           --serving依赖的代码和配置；模型发布后，由该服务提供在线预测
├── mysql_init             --存放数据库初始化的脚本
├── fateflow
├── examples
├── python
├── rust
└── src
```

## 3.    修改配置
这一步非常重要，也是部署工作中最关键的步骤，请仔细进行一一核对。   
> #### SeceumFL的默认配置在以下前提下才能生效：
> - 至少有两台独立IP的物理机形成两个SeceumFL的节点；
> - 每台物理机部署整套服务且都需要调整配置；
> - 下文中标识为‘MY_IP’的地方，都需要用本机IP替换，其他部分可以不修改；
> - 除非端口已经被占用，否则不需修改默认端口。

在配置之前，请先确定部署机器的内网IP，如：192.168.1.20（**MY_IP**）

```shell
ifconfig

ens192: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.20  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 ee80::191a:fc15:c1:f3f7  prefixlen 64  scopeid 0x20<link>
        ether 01:1c:23:71:fc:72  txqueuelen 1000  (Ethernet)
        RX packets 47783624  bytes 57304565627 (53.3 GiB)
        RX errors 0  dropped 639698  overruns 0  frame 0
        TX packets 22938162  bytes 28721703686 (26.7 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
为了配置方便起见，可以先配置**eggroll/conf/route_table.json**，如[3.2](#3.2)所示，将所有参与方的Party ID，IP等都设置好，然后用以下脚本去设置己方的其他配置。    
```shell
python3 ./init_local_ip.py [PartyID]
```
**如果脚本正常运行，可以跳过其它配置的步骤，也可以再检查一下以下的配置信息。**

Note：每个参与方为一个Party，有个全局的Party ID

### 3.1.  主要配置的修改

```properties
SeceumFL/conf/
├── app.config.js                 --web服务所需配置
├── chain_config.yaml
├── fl_config.yaml        
├── pulsar_route_table.yaml
├── rabbitmq_route_table.yaml
├── service_conf.yaml            --Fate服务所需配置
└── ssh.yaml
```
这里主要更改两个文件，**service_conf.yaml**和**app.config.js**。

- **conf/service_conf.yaml**该配置为后端服务**fate_flow_server**的主要配置，只需要对Host进行修改，填入本机IP，修改内容如下所示：

Note：其它部分可以不用修改。

```yaml
 23   dataset: false
 24 fateflow:
 25   # you must set real ip address, 127.0.0.1 and 0.0.0.0 is not supported
 26   host: MY_IP         #这里需要替换成真实IP
 27   http_port: 9380
 28   grpc_port: 9360
 ````
 
- **conf/app.config.js**该配置关系到Web服务是否能连上后端服务，需要填入后端服务所在机器的IP地址，修改内容如下所示：

Note：其他部分可以不用更改。

```javascript
1 window.__PRODUCTION__SECEUMFL__CONF__={
2     "VITE_GLOB_APP_TITLE":"SeceumFL",
3     "VITE_GLOB_APP_SHORT_NAME":"SeceumFL",
4     "VITE_GLOB_PROD_MOCK":"false",
5     "VITE_GLOB_API_URL":"http://MY_IP:9380", /*这里需要替换成真实IP*/
6     "VITE_GLOB_SPCHAIN_API_URL":"http://127.0.0.1:8001",
7     "VITE_GLOB_SERVICE_API_URL":"http://127.0.0.1:8349/service/",
8     "VITE_GLOB_UPLOAD_URL":"","VITE_GLOB_IMG_URL":"","VITE_GLOB_API_URL_PREFIX":""
9 };
10 Object.freeze(window.__PRODUCTION__SECEUMFL__CONF__);Object.defineProperty(window,"__PRODUCTION__SECEUMFL__CONF__",{configurable:false,writable:false,});
```

### 3.2.  Eggroll配置的修改
[Eggroll](https://github.com/FederatedAI/eggroll)的功能主要是联邦通讯、分布式存储和计算，是FATE的主要服务模块，包括：**Rollsite、Clustermanager、Nodemanager**。    

主要修了两个文件：**route_table.json**和**eggroll.properties**。

- **eggroll/conf/route_table.json**该配置存储了联邦节点的路由信息，**所有的联邦节点该配置应该相同**。以下是两个节点的配置，“IP”需改成各参与方真实的物理机IP，其它部分可以不用修改。  
  
```json
{
    "route_table": {
        "default": {
            "default": [
                {
                    "ip": "172.0.0.1",
                    "port": "9370"
                }
            ]
        },
        "9999": { #其中一方的Party ID
            "default": [
                {
                    "ip": "192.168.1.20",  #其中一方的机器IP
                    "port": 9370,
                    "name": "Son"
                }
            ],
            "fateflow": [
                {
                    "ip": "192.168.1.20", #其中一方的机器IP
                    "port": 9360
                }
            ]
        },
        "10000": { #另外一方的Party ID
            "default": [
                {
                    "ip": "192.168.1.216", #另外一方的机器IP
                    "port": 9370,
                    "name": "Dady"
                }
            ],
            "fateflow": [
                {
                    "ip": "192.168.1.216", #另外一方的机器IP
                    "port": 9360
                }
            ]
        }
    },
    "permission": {
        "default_allow": true
    }
}
```
- **eggroll/conf/eggroll.properties**该配置会被三个服务同时使用，必须修改的部分为**Party ID**在每个机器上，以下配置是不同的，需要和**route_table.json**对应。    
```properties
...
31 eggroll.resourcemanager.process.tag=9999
...
71 eggroll.rollsite.party.id=9999
...
```

### 3.3  FATE-Board配置的修改
[FATE-Board](https://github.com/FederatedAI/FATE-Board)是FATE提供查看任务的Web服务模块。    

主要更改的配置文件为： **fateboard/conf/application.properties**，需要将后台服务的IP填入，这里是指本机IP。

```properties
1 server.port=8083 
2 fateflow.url=http://MY_IP:9380
...
```

### 3.3  FATE-Serving配置的修改
[FATE-Serving](https://github.com/FederatedAI/FATE-Serving)，它可基于训练好的模型提供在线推理服务。    

主要更改的配置文件为： **fate-serving/fate-serving-server/conf/serving-server.properties**，需要将后台服务的IP填入，这里是指本机IP。

```properties
...
 42 http.adapter.url=http://MY_IP:9380/v1/model_manage/get_feature
 43 # model transfer
 44 model.transfer.url=http://MY_IP:9380/v1/model/transfer
...
```

## 4.    启动服务
SeceumFL需要启动10个服务，可以用**docker-compose**，但建议逐个启动服务更为妥当。

```shell
cd /home/alice/SeceumFL;
docker-compose up -d
```

### 4.1  周边服务的启动
SeceumFL需要启动3个服务，分别是：**MySQL、Zookeeper、Redis（非必须）**

```shell
docker run --privileged=true -d --name mysql --network=host -v /home/alice/SeceumFL/mysql-data/:/var/lib/mysql:rw -v /home/alice/SeceumFL/mysql_init/:/docker-entrypoint-initdb.d/:rw -v /etc/localtime:/etc/localtime:ro -e MYSQL_ALLOW_EMPTY_PASSWORD="yes" mysql:8.0.28
docker run --privileged=true -d --name zookeeper --user=root --network=host -v /home/alice/zk-data/:/bitnami/zookeeper/data/ -e ALLOW_ANONYMOUS_LOGIN="yes" bitnami/zookeeper:latest
docker run --privileged=true -d --name redis --network=host  redis:6.0.8 redis-server --requirepass nopassword
```

### 4.2  Eggroll的启动
SeceumFL需要启动3个服务，分别是：**Rollsite、clustermanager、nodemanager**

```shell
docker run --privileged=true -d --rm --name rollsite --network=host -v /home/alice/SeceumFL/:/data/projects/fate/ -v /etc/localtime:/etc/localtime:ro seceum-fl:3.2 ./eggroll/bin/start.sh rollsite
docker run --privileged=true -d --rm --name clustermanager --network=host -v /home/alice/SeceumFL/:/data/projects/fate/ -v /etc/localtime:/etc/localtime:ro seceum-fl:3.2 ./eggroll/bin/start.sh clustermanager
docker run --privileged=true -d --rm --name nodemanager --network=host -v /home/alice/SeceumFL/:/data/projects/fate/ seceum-fl:3.2 ./eggroll/bin/start.sh nodemanager
```

### 4.3  WEB服务的启动
SeceumFL需要启动2个服务，分别是：**seceum-fl-web、FATE-Board**

```shell
docker run --privileged=true -d --network=host -v /home/alice/SeceumFL/conf/app.config.js:/data/projects/studio/app.config.js --name seceum-web seceum-fl-web:3.2
docker run --privileged=true -d --rm --name fateboard --network=host -v /home/alice/SeceumFL/:/data/projects/fate/ seceum-fl:3.2 bash ./fateboard/bin/service.sh start
```


### 4.4 FateFlow后台服务的启动
SeceumFL需要启动2个服务，分别是：**fate_flow_server、serving（在线预测）**

```shell
docker run --privileged=true -d --rm --name serving --network=host -v /home/alice/SeceumFL/:/data/projects/fate/ seceum-fl:3.2 bash bin/serving_start.sh
docker run --privileged=true -d --network=host --name fate_flow_server -v /home/alice/SeceumFL/:/data/projects/fate/ --privileged=true seceum-fl:3.2 /data/projects/python/venv/bin/python fateflow/python/fate_flow/fate_flow_server.py
```


## 5.    服务运行状态的确认
- 首先，需要确认一下，以下10个服务是否都已经在线；
- 然后再确认服务的内部状态是否健康，如果没问题，即可进行下一步操作。

```shell
docker ps

CONTAINER ID      IMAGE                         COMMAND                  CREATED           STATUS      NAMES
7f0ce1b40acb      seceum-fl-web:3.2            "/docker-entrypoin..."   3 hours ago       Up 3 hours   seceum-web
38b09a6cf67d      seceum-fl:3.2                "/data/projects/py..."   6 hours ago       Up 3 hours   fate_flow_server
5ae51b0c3577      seceum-fl:3.2                "bash bin/serving_..."   26 hours ago      Up 26 hours  serving
3259f60efb28      seceum-fl:3.2                "/bin/bash"              5 hours ago       Up 5 hours   fateboard
ded5a9773602      seceum-fl:3.2                "./eggroll/bin/sta..."   26 hours ago      Up 4 hours   nodemanager
20b3b2d99406      seceum-fl:3.2                "./eggroll/bin/sta..."   26 hours ago      Up 4 hours   clustermanager
3c6d81d38202      seceum-fl:3.2                "./eggroll/bin/sta..."   26 hours ago      Up 4 hours   rollsite
8f64bfed233c      redis:6.0.8                 "docker-entrypoint..."   26 hours ago      Up 26 hours  redis
781af70bfb83      bitnami/zookeeper:latest    "/opt/bitnami/scri..."   26 hours ago      Up 26 hours  zookeeper
d41250c5676e      mysql:8.0.28                "docker-entrypoint..."   26 hours ago      Up 26 hours  mysql

```
- **如果服务没有在线（docker ps没有显示服务），可以用docker  ps -a，拿到Container ID（如：38b09a6cf67d），重启容器：docker restart 38b09a6cf67d。**

### 5.1  Fateflow的服务状态
首先进入容器内部，如下：

```shell
docker exec -it fate_flow_server /bin/bash
```
进入后，执行以下脚本(gid为当前机器的PartyID， hid为合作方PartyID)，如最后能得到**success**，表明SeceumFL系统已经通过冒烟测试。

```shell
# flow init -c /data/projects/fate/conf/service_conf.yaml 
{
    "retcode": 0,
    "retmsg": "Fate Flow CLI has been initialized successfully."
}

# flow test toy -gid 9999 -hid 10000
toy test job 202306050945229905440 is waiting
toy test job 202306050945229905440 is waiting
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is running
toy test job 202306050945229905440 is success

```
其次，可以查看log，观察服务的状态，log的地址为：**./fateflow/logs/fate_flow**。

### 5.2  Fateboard的服务状态
使用浏览器打开**http://MY_IP:8083/**, 登录名和密码都是**admin**。如能成功登录，且在**JOBS** Tab页看到上一步执行的任务则表示通过测试。

### 5.3  Web服务状态
使用浏览器打开**http://MY_IP:8349/**, 登录名和密码都是**admin**。如能成功登录则表示通过测试。

### 5.4  Serving服务状态
使用浏览器打开**http://MY_IP:8350/**, 登录名和密码都是**admin**。如能成功登录则表示通过测试。

## 6.    其它
对于数据源，系统可以支持接入hive，hbase，hdfs，oracle。此时需要进入容器安装以下依赖：

```shell
docker exec -it fate_flow_server /bin/bash
cd /data/projects/;
curl https://archive.apache.org/dist/hadoop/common/hadoop-3.2.1/hadoop-3.2.1.tar.gz
tar -xf ./hadoop-3.2.1.tar.gz;
rm -fr hadoop-3.2.1.tar.gz;

yum install unzip
curl https://download.oracle.com/otn_software/linux/instantclient/213000/instantclient-basiclite-linux-21.3.0.0.0.zip
unzip instantclient-basiclite-linux-21.3.0.0.0.zip
mv instantclient-basiclite-linux-21.3.0.0.0 instantclient
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/projects/hadoop-3.2.1/lib/native:/data/projects/instantclient
```

