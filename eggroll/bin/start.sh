#!/bin/bash

if [ "$1"x == "rollsite"x ];then
    java -Dlog4j.configurationFile=${EGGROLL_HOME}/conf/log4j2.properties -cp ${EGGROLL_LIB}/*:${EGGROLL_HOME}/conf/ com.webank.eggroll.rollsite.EggSiteBootstrap -c ${EGGROLL_HOME}/conf/eggroll.properties;
elif [ "$1"x == "clustermanager"x ];then
    java -Dlog4j.configurationFile=${EGGROLL_HOME}/conf/log4j2.properties -cp ${EGGROLL_LIB}/*: com.webank.eggroll.core.Bootstrap --bootstraps com.webank.eggroll.core.resourcemanager.ClusterManagerBootstrap -c ${EGGROLL_HOME}/conf/eggroll.properties -p 4670 -s 'EGGROLL_DEAMON';
elif [ "$1"x == "nodemanager"x ];then
    source /data/projects/python/venv/bin/activate
    java -Dlog4j.configurationFile=${EGGROLL_HOME}/conf/log4j2.properties -cp ${EGGROLL_LIB}/*: com.webank.eggroll.core.Bootstrap --bootstraps com.webank.eggroll.core.resourcemanager.NodeManagerBootstrap -c ${EGGROLL_HOME}/conf/eggroll.properties -p 4671 -s 'EGGROLL_DEAMON';
else
    echo "Wrong parameter: $1";
    echo "$0 [rollsite/clustermanager/nodemanager]";
fi
