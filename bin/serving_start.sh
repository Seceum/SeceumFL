#!/bin/bash

cd /data/projects/fate/fate-serving/;
java -Dspring.config.location=fate-serving-server/conf/serving-server.properties -cp fate-serving-server/conf/:/data/projects/serving-server-lib/*:/data/projects/serving-server-lib/fate-serving-server.jar com.webank.ai.fate.serving.Bootstrap &
java -Dspring.config.location=fate-serving-proxy/conf/application.properties -cp fate-serving-proxy/conf/:/data/projects/serving-proxy-lib/*:/data/projects/serving-proxy-lib/fate-serving-proxy.jar com.webank.ai.fate.serving.proxy.bootstrap.Bootstrap &
java -Dspring.config.location=fate-serving-admin/conf/application.properties -cp fate-serving-admin/conf/:/data/projects/serving-admin-lib/*:/data/projects/serving-admin-lib/fate-serving-admin.jar com.webank.ai.fate.serving.admin.Bootstrap &

wait;
