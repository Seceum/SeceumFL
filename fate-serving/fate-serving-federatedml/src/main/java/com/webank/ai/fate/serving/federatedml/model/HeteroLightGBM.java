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

import com.google.common.collect.Maps;
import com.webank.ai.fate.core.mlmodel.buffer.BoostTreeModelMetaProto.BoostingTreeModelMeta;
import com.webank.ai.fate.core.mlmodel.buffer.BoostTreeModelParamProto.BoostingTreeModelParam;
import com.webank.ai.fate.core.mlmodel.buffer.BoostTreeModelParamProto.DecisionTreeModelParam;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

public abstract class HeteroLightGBM extends HeteroSecureBoost {
    public static final Logger logger = LoggerFactory.getLogger(HeteroLightGBM.class);

}

