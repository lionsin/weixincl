from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from oauths.utils import BaseModel


class User(AbstractUser):
    # 声明字段(内置有这些字段)
    # id =models.IntegerField(unique=True, primary_key=True)
    # username = models.CharField(max_length=240, null=False)
    # password = models.
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email = models.EmailField(max_length=20, verbose_name="邮件")
    is_checked = models.BooleanField(default=False, verbose_name="邮箱验证码激活状态")
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="📔余额")

# 常用的密码设置方法
# set_password
# check_passwrod
    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
