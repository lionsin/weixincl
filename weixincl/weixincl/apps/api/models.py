from django.db import models

# Create your models here.

class ParamPass(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="id")
    text = models.CharField(default=" ", max_length=10, verbose_name="查询请求字符串")
    def __str__(self):
        return self.text

    class Meta:
        db_table = "tb_text"
        verbose_name = '查询参数'
        verbose_name_plural = verbose_name

