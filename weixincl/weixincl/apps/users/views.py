import logging

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from users import constants


logger = logging.getLogger("weixincl")

from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from users.serializers import UserSerializer



class MobileCountAPIView(APIView):
    # ...mobile/(?P<mobile>1[3456789]\d{9}/)/count
    def get(self, request, mobile):
        # 尝试从数据库中获取用户
        count= None
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error(e)

        data = {
            "count": count,
            "mobile": mobile
        }

        return Response(data)
#
# # ＝＝＝＝＝＝＝＝＝＝＝＝用户注册视图＝＝＝＝＝＝＝＝＝＝＝
# class UserAPIView(CreateAPIView):
#
#     serializer_class = UserSerializer
#
#
class ListUserCentreInfo(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 判断用户是否登陆
        # print(request.META)
        user = request.user
        # print(user.is_authenticated)
        # print(user)
        print(user.is_checked)
        return Response({
            "id": user.id,
            "username": user.username,
            "mobile": user.mobile,
            "email": user.email,
            "email_active": user.is_checked
        })



#===============用户浏览历史视图＝＝＝＝＝＝＝＝＝＝

# class UserBrowsingHistoryView(CreateAPIView):
#     """用户浏览器商品的视图"""
#     serializer_class = AddUserBrowsingHistorySerializer
#     # permission_classes = [IsAuthenticated]
#     queryset = SKU
#
#     def get(self,request):
#         """获取浏览历史记录"""
#         # 从redis中获取当前用户的user_id
#         user_id = request.user.id
#
#         # 从redis获取浏览历史记录
#         redis_conn = get_redis_connection("history")
#         history = redis_conn.lrange("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)
#
#         skus = []
#         # 为了保持查询出的顺序与用户的浏览历史保存顺序一致
#         for sku_id in history:
#             sku = SKU.objects.get(id=sku_id)
#             skus.append(sku)
#
#         serializer = SKUSerializer(skus, many=True)
#
#         return Response(serializer.data)
