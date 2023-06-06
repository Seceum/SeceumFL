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

import com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionMetaProto;
import com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionMetaProto.FeatureOutliertionMeta;
import com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionParamProto.FeatureOutliertionParam;
import com.webank.ai.fate.serving.core.bean.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FeatureOutlier extends BaseComponent {
    private static final Logger logger = LoggerFactory.getLogger(FeatureOutlier.class);
    private FeatureOutliertionParam featureOutliertionParam;
    private FeatureOutliertionMeta featureOutliertionMeta;
    private Map<String, String> replaceValueMap;;
    private Map<String, String> replaceTypeMap;
    private List<String> skipCols;
    private Map<String, FeatureOutliertionMetaProto.list> outlierRange;
    private boolean needRun;

    @Override
    public int initModel(byte[] protoMeta, byte[] protoParam) {
        logger.info("start init Feature Selection class");
        this.needRun = false;
        try {
            this.featureOutliertionMeta = this.parseModel(FeatureOutliertionMeta.parser(), protoMeta);
            this.needRun = this.featureOutliertionMeta.getNeedRun();
            this.featureOutliertionParam = this.parseModel(FeatureOutliertionParam.parser(), protoParam);
            this.replaceValueMap = featureOutliertionParam.getImputerParam().getMissingReplaceValueMap();
            this.replaceTypeMap = featureOutliertionParam.getImputerParam().getMissingReplaceValueTypeMap();
            this.skipCols = featureOutliertionParam.getImputerParam().getSkipColsList();
            this.outlierRange = featureOutliertionMeta.getImputerMeta().getMissingValue();
        } catch (Exception ex) {
            ex.printStackTrace();
            return ILLEGALDATA;
        }
        logger.info("Finish init Feature Outlier class");
        return OK;
    }

    @Override
    public Object getParam() {
//        return JsonUtil.object2Objcet(featureSelectionParam, new TypeReference<Map<String, Object>>() {});
        return featureOutliertionParam;
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
            try {
                v = Double.parseDouble(v.toString());
            }catch (Exception e){
                outputData.put(key, v);
                continue;
            }
            if (!(this.skipCols!=null && this.skipCols.contains(key))
                    && this.replaceValueMap != null && this.replaceValueMap.containsKey(key) && this.replaceValueMap.get(key)!=null
                    && this.outlierRange != null && this.outlierRange.containsKey(key) && this.outlierRange.get(key)!=null && this.outlierRange.get(key).getValueList().size() == 2
                    && ((double)v < this.outlierRange.get(key).getValue(0) || (double)v > this.outlierRange.get(key).getValue(1))){
                v = Double.parseDouble(this.replaceValueMap.get(key));
            }
            outputData.put(key, v);
        }
        return outputData;
    }
}
