from django.contrib import admin

# Register your models here.
from weixin.models import PublicNum, Article,CollectTask

admin.site.register(PublicNum)
admin.site.register(Article)
admin.site.register(CollectTask)