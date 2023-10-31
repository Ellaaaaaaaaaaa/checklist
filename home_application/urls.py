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

from django.conf.urls import url

from . import views

urlpatterns = (
    url(r"^$", views.home),


    # 操作记录
    url(r"^job_center/$", views.job_center, name="任务中心页面"),
    url(r"^job_details/$", views.job_details, name="任务详情页面"),
    url(r"^job_details2/$", views.job_details2, name="任务详情2页面"),

    # 查询模板
    url(r"^get_template_list/$", views.get_template_list, name="显示（所有）模板"),
    url(r"^create_template/$", views.create_template, name="新建模板"),
    url(r'^delete_template/(?P<template_id>[-\w]+)/$', views.delete_template, name="删除模板"),
    url(r'^download_template/(?P<template_id>[-\w]+)/$', views.download_template, name="下载模板"),
    url(r'^get_template_info_by_name/(?P<template_id>[-\w]+)/$', views.get_template_info_by_name, name="获取模板信息"),

    # 任务逻辑
    url(r"^get_job_list/$", views.get_job_list, name="显示（所有）任务"),
    url(r'^create_todo_job/$', views.create_todo_job, name="新建任务"),

    url(r"^get_job_detail_list/(?P<operator_id>[-\w]+)/$", views.get_job_detail_list, name="显示所有子任务"),
    url(r"^get_job_detail_list_operate/(?P<operator_id>[-\w]+)/$", views.get_job_detail_list_operate, name="显示所有子任务"),

    url(r"^pass_state_by_order/(?P<order>[-\w]+)/$", views.pass_state_by_order, name="传递序号"),

    url(r"^edit_job_detail_state/(?P<operator_id>[-\w]+)/$", views.edit_job_detail_state, name="修改子任务状态"),

)
