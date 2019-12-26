#　创建模型对象系列化器
import re
from celery_tasks.emails.tasks import send_verify_email
from django.conf import settings

import logging


from users import constants
from django_redis import get_redis_connection
from rest_framework.response import Response

logger = logging.getLogger("weixincl")
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    password2 = serializers.CharField(label="确认密码", max_length=128, min_length=6, write_only=True)
    allow = serializers.BooleanField(label="是否同意协议", required=True, write_only=True)
    # token = serializers.CharField(max_length=64, write_only=True, label="登录状态token")
    class Meta:
        model = User
        fields = ["id", "username", "password", "password2", "sms_code", "allow", "mobile"]

    def validate_allow(self, value):

        if value != True:
            # print(type(value))
            raise serializers.ValidationError("协议不能为空")

    def validate_mobile(self, value):
        user = None
        if not re.match(r"^1[3456789]\d{9}", value):
            raise serializers.ValidationError("输入的手机号码不正确")
        try:
            user = User.objects.filter(mobile=value).count()
        except Exception as e:
            logger.error({"message": "获取数据失败"})
            raise serializers.ValidationError("获取用户数据失败")
        if user > 0:
             raise serializers.ValidationError("用户名已存在")

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        # if not re.match(r"\w{5,12}", password):
        #     raise serializers.ValidationError("密码格式有误")
        # if not re.match(r"\w{5,12}", password2):
        #     raise serializers.ValidationError("密码格式有误")
        if password != password2:
            raise serializers.ValidationError("密码不一致")
        mobile = attrs["mobile"]
        sms_code = attrs["sms_code"]
        print(sms_code)
        redis_sms_code = get_redis_connection("verify")
        try:
            real_sms_code = redis_sms_code.get("sms_%s" % mobile).decode()
        except Exception:
            raise serializers.ValidationError("获取短信验证码失败！")
        if sms_code != real_sms_code:
            raise serializers.ValidationError("短信验证失败")

        return attrs

    def create(self, validated_data):

        # 删除只写校验数据
        del validated_data["sms_code"]
        del validated_data["allow"]
        del validated_data["password2"]


        # 新增用户
        user = super().create(validated_data)
        # 对密码进行加密处理
        user.set_password(validated_data["password"])
        # 保存数据
        user.save()

        # 注册成功了，使用jwt保存登陆状态


        # # 获取 生成载荷的函数
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # # 获取 生成token的函数
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        #
        # payload = jwt_payload_handler(user)
        # token = jwt_encode_handler(payload)
        #
        # user.token = token

        # 返回用户
        return user




# class AddUserBrowsingHistorySerializer(serializers.Serializer):
#     """浏览历史的序列化器"""
#     sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)
#
#     def validate_sku_id(self, value):
#         """
#         检验sku_id是否存在
#         """
#         try:
#             SKU.objects.get(id=value)
#         except SKU.DoesNotExist:
#             raise serializers.ValidationError('该商品不存在')
#         return value
#
#     def create(self,validated_data):
#         # 获取当前登陆的用户id
#         user_id = self.context['request'].user.id
#         sku_id = validated_data['sku_id']
#         """redis中保存历史记录的数据类型格式
#
#         例如，本次用户访问的sku是2,
#
#         user_id: [
#            7,6,1,4,2
#         ]
#         """
#         # 把sku_id保存redis的list类型数据中
#         redis_conn = get_redis_connection("history")
#         pl = redis_conn.pipeline()
#         # 删除redis中同样的sku_id,
#         pl.lrem("history_%s" % user_id, 0, sku_id)
#         # 然后添加sku_id到redis
#         pl.lpush("history_%s" % user_id, sku_id)
#         # 如果超过最大长度，则最后一个成员要被剔除
#         pl.ltrim("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)
#         pl.execute()
#
#         return validated_data