/*
 * Copyright 2019 The FATE Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.webank.ai.fate.serving.federatedml.model;

import com.webank.ai.fate.core.mlmodel.buffer.FeatureImputationMetaProto.FeatureImputationMeta;
import com.webank.ai.fate.core.mlmodel.buffer.FeatureImputationParamProto.FeatureImputationParam;
import com.webank.ai.fate.serving.core.bean.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FeatureImputation extends BaseComponent {
    private static final Logger logger = LoggerFactory.getLogger(FeatureImputation.class);
    private FeatureImputationParam featureImputationParam;
    private FeatureImputationMeta featureImputationMeta;
    private Map<String, String> replaceValueMap;;
    private Map<String, String> replaceTypeMap;
    private List<String> skipCols;
    private List<String> asMissValue;
    private boolean needRun;

    @Override
    public int initModel(byte[] protoMeta, byte[] protoParam) {
        logger.info("start init Feature Selection class");
        this.needRun = false;
        try {
            this.featureImputationMeta = this.parseModel(FeatureImputationMeta.parser(), protoMeta);
            this.needRun = this.featureImputationMeta.getNeedRun();
            this.featureImputationParam = this.parseModel(FeatureImputationParam.parser(), protoParam);
            this.replaceValueMap = featureImputationParam.getImputerParam().getMissingReplaceValueMap();
            this.replaceTypeMap = featureImputationParam.getImputerParam().getMissingReplaceValueTypeMap();
            this.skipCols = featureImputationParam.getImputerParam().getSkipColsList();
            this.asMissValue = featureImputationMeta.getImputerMeta().getMissingValueList();
        } catch (Exception ex) {
            ex.printStackTrace();
            return ILLEGALDATA;
        }
        logger.info("Finish init Feature Selection class");
        return OK;
    }

    @Override
    public Object getParam() {
//        return JsonUtil.object2Objcet(featureSelectionParam, new TypeReference<Map<String, Object>>() {});
        return featureImputationParam;
    }

    @Override
    public Map<String, Object> localInference(Context context, List<Map<String, Object>> inputData) {
        HashMap<String, Object> outputData = new HashMap<>(8);
        Map<String, Object> firstData = inputData.get(0);
        if (!this.needRun) {
            return firstData;
        }
        for (String key : firstData.keySet()) {
            Object v = firstData.get(key);
            if (!(this.skipCols!=null && this.skipCols.contains(key))
                    && this.replaceValueMap != null && this.replaceValueMap.containsKey(key) && this.replaceValueMap.get(key)!=null
                    && (v == null || v.toString().isEmpty() || (this.asMissValue!=null && this.asMissValue.contains(v.toString()))
                        || v.toString().equalsIgnoreCase("null") || v.toString().equalsIgnoreCase("none"))) {
                String vv = this.replaceValueMap.get(key);
                String type = "str";
                if (this.replaceTypeMap!=null && this.replaceTypeMap.containsKey(key)) type = this.replaceTypeMap.get(key);
                switch (type){
                    case "float": v = Float.parseFloat(vv);break;
                    case "int": v = Integer.parseInt(vv);break;
                    case "bool": v = Boolean.parseBoolean(vv);break;
                    default: break;
                }
            }
            outputData.put(key, v);
        }
        return outputData;
    }
}
