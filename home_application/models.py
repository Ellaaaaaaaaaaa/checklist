# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

# from django.db import models

# Create your models here.
# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models
from datetime import datetime

# Create your models here.
from django.db import models

TEMPLATE_CHOICES = [(0, "变更发布"), (1, "扩缩类"), (2, "上线类"), (3, "下架类"), (4, "例行维护")]
BUSINESS_CHOICES = [(0, "小游戏教学演示")]


class Records(models.Model):
    operator = models.CharField(verbose_name="操作人", max_length=128)
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    operate_action = models.CharField(verbose_name="操作内容", max_length=255)
    operate_status = models.CharField(verbose_name="操作结果", max_length=255)
    create_time = models.DateTimeField(verbose_name="日志创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="日志更新时间", auto_now=True)
    is_deleted = models.BooleanField(verbose_name="逻辑删除", default=False)
    input_params = models.JSONField(null=True, verbose_name="请求参数")
    output_params = models.JSONField(null=True, verbose_name="输出参数")


class Templates(models.Model):
    """
    模板信息表
    """

    template_name = models.CharField(verbose_name="模板名称", max_length=255)
    business_name = models.IntegerField(verbose_name="业务名称", choices=BUSINESS_CHOICES)
    template_type = models.IntegerField(verbose_name="模板类型", choices=TEMPLATE_CHOICES)
    creator = models.CharField(verbose_name="创建者", max_length=255)
    updator = models.CharField(verbose_name="更新者", max_length=255)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    # template_content = models.ForeignKey(TemplateContents, on_delete=models.CASCADE)


class TemplateContents(models.Model):
    """
    模板内容表
    """
    belong_template = models.ForeignKey(Templates, on_delete=models.CASCADE)
    order = models.IntegerField(verbose_name="序号")
    operation = models.CharField(verbose_name="操作事项", max_length=255)
    operation_note = models.CharField(verbose_name="备注", max_length=255)
    person_responsible = models.CharField(verbose_name="负责人", max_length=128)


class Jobs(models.Model):
    """
    任务信息表
    """
    STATE_CHOICES = [(1, "待操作"), (2, "操作中"), (3, "完成")]
    template_name = models.CharField(verbose_name="模板名称", max_length=255)
    business_name = models.IntegerField(verbose_name="业务名称", choices=BUSINESS_CHOICES)
    template_type = models.IntegerField(verbose_name="模板类型", choices=TEMPLATE_CHOICES)
    operator_id = models.CharField(verbose_name="操作识别号", max_length=255)
    person_couldOperate = models.CharField(verbose_name="可操作者", max_length=255)
    creator = models.CharField(verbose_name="创建者", max_length=255)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    STATE = models.IntegerField(verbose_name="状态", choices=STATE_CHOICES, default=1)
    # job_content = models.ForeignKey(JobContents, on_delete=models.CASCADE)


class JobContents(models.Model):
    """
    任务内容表
    """
    belong_job = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    order = models.IntegerField(verbose_name="序号")
    operation = models.CharField(verbose_name="操作事项", max_length=255)
    operation_note = models.CharField(verbose_name="备注", max_length=255)
    finish_time = models.DateTimeField(verbose_name="完成时间", default=None, null=True, blank=True)
    person_responsible = models.CharField(verbose_name="负责人", max_length=128)
    person_confirm = models.CharField(verbose_name="确认人", max_length=128, default="")
    state = models.BooleanField(verbose_name="是否完成", default=False)


