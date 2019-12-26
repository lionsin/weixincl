from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from weixin.models import PublicNum
from weixin.serializers import PcNumSerializer


class PassParamsSerializer(serializers.Serializer):
    text = serializers.CharField(label='参数', max_length=10)


class SavePcSerializer(serializers.Serializer):
    """
    保存公众号
    """
    """
    数据格式：
      {
        "pc_list": [
    {
    "image_url":"weixin/0.jpg",
    "_biz":"ssds",
    "name":"sdsad",
    "introduction":"24324",
    "weixin_num":"sadasd"
    },
    {
    "image_url":"weixin/4.jpg",
    "_biz":"ssdss",
    "name":"sdssad",
    "introduction":"24s324",
    "weixin_num":"sadsasd"
    }
    ]
    }    
    """
    pc_list = serializers.ListField(label="返回的微信公众号列表", allow_empty=False, max_length=100)
    def validate(self, attrs):
        pc_list = attrs["pc_list"]
        if not pc_list:
            raise serializers.ValidationError("返回的数据不能为空")
        return attrs
    def create(self, validated_data):
        # user = self.context['request'].user
        # timezone.now() -> datetime
        pc_list_to_insert = list()
        pc_list = validated_data['pc_list']
        # print(type(pc_list))

        for pc in pc_list:
            # 已经存在的公众号不插入
            if not PublicNum.objects.filter(name=pc["name"]):
                p = PublicNum(name=pc["name"], image_url=pc["image_url"], _biz=pc["_biz"], introduction=pc["introduction"],
                                         weixin_num=pc["weixin_num"])
                pc_list_to_insert.append(p)
        try:
            # 批量插入微信公众号
            PublicNum.objects.bulk_create(pc_list_to_insert)
        except ValidationError:
            raise
        return validated_data
