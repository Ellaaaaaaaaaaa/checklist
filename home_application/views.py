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
import datetime

import json
import logging
import os.path
from io import BytesIO

import xlrd, xlwt
from django.db import transaction
from django.utils.http import urlquote

from blueking.component.shortcuts import get_client_by_request
from django.core.paginator import Paginator
from django.shortcuts import render
from django.template.defaulttags import register
from django.http import JsonResponse, HttpResponseNotAllowed, FileResponse, HttpResponse
from .models import Templates, TemplateContents, Jobs, JobContents

from django.conf import settings
from blueapps import account

logger = logging.getLogger('auditLogger')

"""
    配置平台接口信息
    https://apigw.ce.bktencent.com/docs/component-api/default/CC/intro
"""
OS_TYPE = {"1": "Linux", "2": "Windows", "3": "AIX"}
PLATFORMS = dict([
    ("cmdb", "配置平台"),
    ("jobs", "作业平台"),
    ("monitor", "监控平台"),
    ("sops", "运维平台")
])
OPER_METHOD = dict([
    ("POST", "新增"),
    ("DELETE", "删除"),
    ("PATCH", "修改")
])

# 模板类型
TEMPLATE_CHOICES = {0: "变更发布", 1: "扩缩类", 2: "上线类", 3: "下架类", 4: "例行维护"}
BUSINESS_CHOICES = {0: "小游戏教学演示"}
STATE_CHOICES = {1: "待操作", 2: "操作中", 3: "完成"}


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页  任务模板页
    """
    if request.GET.get("is_vue") == "1":
        return render(request, "home_application/index_vue.html")
    return render(request, "home_application/任务模板.html", {"os_type": json.dumps(OS_TYPE)})


def job_details(request):
    """
    任务详情页面
    """
    return render(request, "home_application/任务详情.html")

def job_details2(request):
    """
    任务详情页面
    """
    return render(request, "home_application/任务详情2.html")


# 编写自定义模板过滤
@register.filter
def get_item(dict: dict, key):
    return dict.get(key, key)




def job_center(request):
    """
    任务中心页面
    """
    return render(request, "home_application/任务中心.html")


def get_template_info_by_name(request, template_id):
    """
    在模板的新建任务框中获取模板信息
    """
    try:
        template_obj = Templates.objects.get(template_name=template_id)
        return JsonResponse(
            {
                "result": True, "code": 200,
                "data": {
                    "info": {
                        'data':
                            {
                                "business_name": template_obj.get_business_name_display(),
                                "template_type": template_obj.get_template_type_display(),
                                "template_name": template_obj.template_name,
                            }
                    }
                }
            }
        )
    except Exception:
        return JsonResponse({"result": False, "code": 101, "message": "获取数据失败"})


def create_todo_job(request):
    """
    创建待办任务
    """
    try:
        template_name = request.POST.get('template_cur_name')
        template_obj = Templates.objects.get(template_name=template_name)
        business_name = template_obj.business_name
        template_type = template_obj.template_type
        creator = request.user.username
        person_couldOperate = request.user.username
        STATE = 1
        create_time = datetime.datetime.now()
        operator_id = request.POST.get('operator_id')

        kwargs = {
            "business_name": business_name,
            "template_type": template_type,
            "template_name": template_name,
            "creator": creator,
            "person_couldOperate": person_couldOperate,
            "create_time": create_time,
            "operator_id": operator_id,
            "STATE": STATE,
        }
    except Exception:
        return JsonResponse({"result": False, "code": 101, "message": "参数获取错误"})

    # 新增数据
    Jobs.objects.create(**kwargs)
    tem = template_obj.templatecontents_set.all()
    for i in tem:  # 逐行读取
        order = i.order
        operation = i.operation
        operation_note = i.operation_note
        person_responsible = i.person_responsible
        kwargs_for_content = {
            "order": order,
            "operation": operation,
            "operation_note": operation_note,
            "person_responsible": person_responsible,
            "belong_job": Jobs.objects.get(operator_id=operator_id),  # 与所属模板建立关联
        }
        JobContents.objects.create(**kwargs_for_content)  # 创建

    return JsonResponse({"result": True, "code": 200, "message": "success"})


def create_template(request):
    """
    新建模板
    """
    # try:
    business_name = int(request.POST.get('business_name'))
    template_type = int(request.POST.get('template_type'))
    template_name = request.POST.get('template_name')
    creator = request.user.username
    updator = request.user.username
    create_time = datetime.datetime.now()
    update_time = datetime.datetime.now()
    # 导入模板
    file = request.FILES.get("template_content")
    if file:
        workbook = xlrd.open_workbook(file_contents=file.read())
        try:
            template_content = workbook.sheet_by_index(0)
            totalrows = template_content.nrows  # 获取总行数
        except Exception:
            return JsonResponse({"result": False, "code": 101, "message": "文件读取失败"})
    else:
        return JsonResponse({"result": False, "code": 101, "message": "文件错误"})
    kwargs = {
        "business_name": business_name,
        "template_type": template_type,
        "template_name": template_name,
        "creator": creator,
        "updator": updator,
        "create_time": create_time,
        "update_time": update_time,
    }
    # except Exception:
    #     return JsonResponse({"result": False, "code": 101, "message": "模板参数获取错误"})
    template_id = request.POST.get("template_id", None)

    if template_id:
        # 修改数据
        try:
            Templates.objects.filter(id=template_id).update(**kwargs)

        except Exception:
            return JsonResponse({"result": False, "code": 101, "message": "error1"})
    else:
        # 新增数据
        # try:
            Templates.objects.create(**kwargs)
            for i in range(totalrows):  # 逐行读取
                order = i + 1
                operation = template_content.row(i)[0].value
                operation_note = template_content.row(i)[1].value
                person_responsible = template_content.row(i)[2].value
                kwargs_for_content = {
                    "order": order,
                    "operation": operation,
                    "operation_note": operation_note,
                    "person_responsible": person_responsible,
                    "belong_template": Templates.objects.get(template_name=template_name),  # 与所属模板建立关联
                }
                TemplateContents.objects.create(**kwargs_for_content)  # 创建
        # except Exception:
            #return JsonResponse({"result": False, "code": 101, "message": "error2"})
    return JsonResponse({"result": True, "code": 200, "message": "success"})


def delete_template(request, template_id):
    """
    删除模板数据
    """
    try:
        with transaction.atomic():
            template_obj = Templates.objects.get(template_name=template_id)
            template_obj.delete()
    except Exception:
        return JsonResponse({"result": False, "code": 101, "message": "删除数据失败"})
    return JsonResponse(
        {
            "result": True, "code": 200,
            "message": "success"
        }
    )


def get_template_list(request):
    """
    获取模板信息列表数据
    """
    # 获取操作次数
    draw = int(request.POST.get("draw"))
    # 获取起始位置
    start = int(request.POST.get("start"))

    # 按条件查询
    kwargs = {}
    if request.POST.get("search_business_name", "") and int(request.POST.get("search_business_name", "")) != -1:
        kwargs.update({"business_name": int(request.POST.get("search_business_name"))})
    if request.POST.get("search_template_type", "") and int(request.POST.get("search_template_type", "")) != -1:
        kwargs.update({"template_type": int(request.POST.get("search_template_type"))})
    if request.POST.get("search_template_name", ""):
        kwargs.update({"template_name__contains": request.POST.get("search_template_name")})  # __contains运算符代表模糊查询
    templates = Templates.objects.filter(**kwargs)
    total = len(templates)
    page_length = int(request.POST.get("length"))
    page = start / page_length + 1

    paginator = Paginator(templates, page_length)
    templates = paginator.get_page(page)
    result_data = []

    # 序列化
    for template_item in templates:
        result_data.append(
            {
                "business_name": BUSINESS_CHOICES.get(template_item.business_name),
                "template_name": template_item.template_name,
                "template_type": TEMPLATE_CHOICES.get(template_item.template_type),
                "creator": template_item.creator,
                "updator": template_item.updator,
                "create_time": template_item.create_time.strftime('%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                "update_time": template_item.update_time.strftime('%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                # "template_content": template_item.template_content,
            }
        )
    return JsonResponse(
        {
            "result": True,
            "code": 200,
            "message": "success",
            "data": {
                "info": {
                    'data': result_data,
                    "recordsTotal": total,
                    "recordsFiltered": total,
                    "draw": draw,
                }
            }
        }
    )


def get_job_list(request):
    """
    获取任务列表数据
    """
    # 获取操作次数
    draw = int(request.POST.get("draw"))
    # 获取起始位置
    start = int(request.POST.get("start"))

    # 按条件查询
    kwargs = {}
    if request.POST.get("search_business_name", "") and int(request.POST.get("search_business_name", "")) != -1:
        kwargs.update({"business_name": int(request.POST.get("search_business_name"))})
    if request.POST.get("search_template_type", "") and int(request.POST.get("search_template_type", "")) != -1:
        kwargs.update({"template_type": int(request.POST.get("search_template_type"))})
    if request.POST.get("search_job_status", "") and int(request.POST.get("search_job_status", "")) != -1:
        kwargs.update({"STATE": int(request.POST.get("search_job_status"))})
    if request.POST.get("search_template_name", ""):
        kwargs.update({"template_name__contains": request.POST.get("search_template_name")})  # __contains运算符代表模糊查询
    if request.POST.get("search_creator", ""):
        kwargs.update({"creator__contains": request.POST.get("search_creator")})  # __contains运算符代表模糊查询
    if request.POST.get("search_operator_id", ""):
        kwargs.update({"operator_id__contains": request.POST.get("search_operator_id")})  # __contains运算符代表模糊查询

    jobs = Jobs.objects.filter(**kwargs)
    total = len(jobs)
    page_length = int(request.POST.get("length"))
    page = start / page_length + 1

    paginator = Paginator(jobs, page_length)
    jobs = paginator.get_page(page)
    result_data = []
    kwargs = {}

    # 序列化
    for job_item in jobs:
        if not Jobs.objects.get(operator_id=job_item.operator_id).jobcontents_set.all().filter(state=False) :
            status = 3
        elif Jobs.objects.get(operator_id=job_item.operator_id).jobcontents_set.all().filter(state=True):
            status = 2
        else:
            status = 1
        kwargs = {
            "template_name": job_item.template_name,
            "business_name": job_item.business_name,
            "template_type": job_item.template_type,
            "operator_id": job_item.operator_id,
            "person_couldOperate": job_item.person_couldOperate,
            "creator": job_item.creator,
            "create_time": job_item.create_time,
            "STATE": status,
        }
        result_data.append(
            {
                "template_name": job_item.template_name,
                "business_name": BUSINESS_CHOICES.get(job_item.business_name),
                "template_type": TEMPLATE_CHOICES.get(job_item.template_type),
                "operator_id": job_item.operator_id,
                "person_couldOperate": job_item.person_couldOperate,
                "creator": job_item.creator,
                "create_time": job_item.create_time.strftime('%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                "STATE": status,
            }
        )
        Jobs.objects.filter(operator_id=job_item.operator_id).update(**kwargs)
    return JsonResponse(
        {
            "result": True,
            "code": 200,
            "message": "success",
            "data": {
                "info": {
                    'data': result_data,
                    "recordsTotal": total,
                    "recordsFiltered": total,
                    "draw": draw,
                }
            }
        }
    )


def get_job_detail_list(request, operator_id):
    """
    获取子任务信息列表数据
    """
    # 获取操作次数
    draw = int(request.POST.get("draw"))
    # 获取起始位置
    start = int(request.POST.get("start"))

    # 根据操作识别号查询
    job_obj = Jobs.objects.get(operator_id=operator_id)
    job_item = job_obj.jobcontents_set.all()

    total = len(job_item)
    page_length = int(request.POST.get("length"))
    page = start / page_length + 1

    paginator = Paginator(job_item, page_length)
    job_item = paginator.get_page(page)
    result_data = []

    # 序列化
    for item in job_item:
        result_data.append(
            {
                "order": item.order,
                "operation": item.operation,
                "operation_note": item.operation_note,
                "finish_time": item.finish_time if item.finish_time is None else item.finish_time.strftime('%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                "person_responsible": item.person_responsible,
                "person_confirm": item.person_confirm,
                "state": "完成" if item.state else "未完成",
            }
        )
    return JsonResponse(
        {
            "result": True,
            "code": 200,
            "message": "success",
            "data": {
                "info": {
                    'data': result_data,
                    "recordsTotal": total,
                    "recordsFiltered": total,
                    "draw": draw,
                }
            }
        }
    )


def edit_job_detail_state(request, operator_id ):
    # 根据操作识别号查询
    job_obj = Jobs.objects.get(operator_id=operator_id)
    job_item = job_obj.jobcontents_set.all()
    order = request.POST.get("order")
    finish_time = datetime.datetime.now()
    person_confirm = request.user.username
    state = True
    kwargs = {
        "finish_time": finish_time,
        "person_confirm": person_confirm,
        "state": state,
    }
    job_item.filter(order=order).update(**kwargs)
    return JsonResponse({"result": True, "code": 200, "message": "success"})


def get_job_detail_list_operate(request, operator_id):
    """
    获取子任务信息列表数据
    """
    # 获取操作次数
    draw = int(request.POST.get("draw"))
    # 获取起始位置
    start = int(request.POST.get("start"))

    # 根据操作识别号查询
    job_obj = Jobs.objects.get(operator_id=operator_id)
    job_item = job_obj.jobcontents_set.all()

    total = len(job_item)
    page_length = int(request.POST.get("length"))
    page = start / page_length + 1

    paginator = Paginator(job_item, page_length)
    job_item = paginator.get_page(page)
    result_data = []

    # 序列化
    for item in job_item:
        result_data.append(
            {
                "order": item.order,
                "operation": item.operation,
                "operation_note": item.operation_note,
                "finish_time": item.finish_time if item.finish_time is None else item.finish_time.strftime('%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                "person_responsible": item.person_responsible,
                "person_confirm": item.person_confirm,
                "state": item.state,
            }
        )
    return JsonResponse(
        {
            "result": True,
            "code": 200,
            "message": "success",
            "data": {
                "info": {
                    'data': result_data,
                    "recordsTotal": total,
                    "recordsFiltered": total,
                    "draw": draw,
                }
            }
        }
    )


def pass_state_by_order(request, order):
    """
    将任务详情里的任务序号传递
    """
    try:
        return JsonResponse(
            {
                "result": True, "code": 200,
                "data": {
                    "info": {
                        'data':
                            {
                                "order": order,
                            }
                    }
                }
            }
        )
    except Exception:
        return JsonResponse({"result": False, "code": 101, "message": "获取数据失败"})


def download_template(request, template_id):
    """
    下载模板数据
    """
    try:
        template_obj = Templates.objects.get(template_name=template_id)
        tem = template_obj.templatecontents_set.all()

        filename = urlquote(template_obj.template_name)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=%s.xls' % filename

        new_excel = xlwt.Workbook()
        new_table = new_excel.add_sheet(template_obj.template_name)

        # 设置宽度
        new_table.col(0).width = 2000
        new_table.col(1).width = 12000
        new_table.col(2).width = 12000
        new_table.col(3).width = 3000

        for i in tem:  # 逐行写入
            new_table.write(i.order-1, 0, i.order)
            new_table.write(i.order-1, 1, i.operation)
            new_table.write(i.order-1, 2, i.operation_note)
            new_table.write(i.order-1, 3, i.person_responsible)

        output = BytesIO()
        new_excel.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response
    except Exception:
        return JsonResponse({"result": False, "code": 101, "message": "模板下载失败"})
