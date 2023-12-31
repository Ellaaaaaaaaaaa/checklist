# Generated by Django 3.2.4 on 2023-06-04 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Records',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.CharField(max_length=128, verbose_name='操作人')),
                ('operate_time', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
                ('operate_action', models.CharField(max_length=255, verbose_name='操作内容')),
                ('operate_status', models.CharField(max_length=255, verbose_name='操作结果')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='日志创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='日志更新时间')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='逻辑删除')),
                ('input_params', models.JSONField(null=True, verbose_name='请求参数')),
                ('output_params', models.JSONField(null=True, verbose_name='输出参数')),
            ],
        ),
    ]
