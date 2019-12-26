import base64
import json
import pickle
import time

from django.conf.urls import url
from django.db.models import Avg
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status

from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import ParamPass
from weixin import constants
from weixin.models import PublicNum, CollectTask, Article
from weixin.serializers import PcNumSerializer, AddCollectListSerializer, TaskSerializer, CollectTaskSerializer, \
    TaskShowDetailSerializer, ArticleShowDetailSerializer, PcSearchHistorySerializer


# ---------------公众号搜索框---------------
class PcSearchListView(ListAPIView):
    """
    搜索框公众号列表数据
    """
    serializer_class = PcNumSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', )

    def get_queryset(self):

        name = self.request.query_params.get("text")
        # sql_str = "SELECT * FROM `tb_pc_nums` WHERE `name` LIKE BINARY %%S% "
        # # 模糊查询查找出符合公众号的数据
        # tr = PublicNum.objects.raw(sql_str, [name])
        query_set = PublicNum.objects.filter(name__icontains=name)
        # 数据库查询不到数据
        if not query_set:
            # 把参数存在参数表中，爬虫不断调用后端
            param = ParamPass.objects.create(text=name)
            # 爬虫爬到的数据村到数据表中，接口地址：//pc/addlist
            time.sleep(1)
            # 不断尝试从数据库中获取数据
            while True:
                try:
                    query_set = PublicNum.objects.filter(name__icontains=name)
                except Exception:
                    continue
            # 将参数表中相对应数据删除
            param.delete()
            # 返还查询结果
            return query_set




            # 爬虫返回数据

            # 存进数据库


        else:
            # 找到想要的数据
            return query_set


# --------------添加采集列表页-------------
class AddCollectList(CreateAPIView):
    """
    获取采集列表 POST /collect_list/
    """
    serializer_class = AddCollectListSerializer
    # permission_classes = [IsAuthenticated]
    queryset = PublicNum.objects.all()
    def get(self, request):
        """获取采集列表"""

        print(222)
        # 从redis中获取当前用户的user_id
        user_id = 1
        # user_id = request.user.id

        # 从redis获取浏览历史记录
        redis_conn = get_redis_connection("collect_list")
        collect_list = redis_conn.lrange("collect_%s" % user_id, 0, constants.USER_COLLECT_HISTORY_COUNTS_LIMIT - 1)

        print(collect_list)
        collect_lists = []
        # 为了保持查询出的顺序与用户的操作保存顺序一致
        for pc_id in collect_list:
            pc = PublicNum.objects.get(id=int(pc_id))
            print(pc.image_url)
            collect_lists.append(pc)
        # print(collect_lists)
        serializer = PcNumSerializer(collect_lists, many=True)
        print(serializer.data)
        return Response(serializer.data)

# ----------------删除选中微信号--------------

class DeleteCollectPC(APIView):
    # collect_list/delete?pc_id=xxxx
    def get(self, request):
        # user = request.user
        user_id = 1
        pc_id = request.query_params.get("pc_id")
        redis_conn = get_redis_connection("collect_list")
        pl = redis_conn.pipeline()
        pl.lrem("collect_%s" % user_id, 0, pc_id)
        return Response({"message": "删除成功"}, status=status.HTTP_204_NO_CONTENT)

# --------------清空采集列表页-----------------
class ClearCollectList(APIView):
    # /collect_list/clear
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        # 获取当前用户
        # user = request.user
        # 查询redis，找到数据
        user_id = 1
        redis_conn = get_redis_connection("collect_list")
        pl = redis_conn.pipeline()
        # 删除redis中所有的_id,
        pl.delete("collect_%s" % user_id)

        return Response({"message": "删除成功"}, status=status.HTTP_204_NO_CONTENT)

# -----------------搜索历史页(cookies)-----------------

class PcSearchHistoryView(APIView):

    # /history/
    def get(self, request):
        """
        查看用户搜索历史
        """
        # try:
        #     user = request.user
        # except Exception:
        #     raise
        user_id = 1

        historys = request.COOKIES.get("history_%s" % user_id)
        print(historys)
        if historys is not None:

            historys = pickle.loads(base64.b64decode(historys.encode()))
        else:
            historys = []
        # 遍历处理历史数据
        """
                           history_userid = [
                   {        "pc_id":pc_id
                           "image_url": "wwww,ss",
                           "name": "sss"
                       },
                            "pc_id": pc_id
                           "image_url": "wwww,ss",
                                   "name": "sss"              
                   }
               ] 
                       """
        serializer = PcSearchHistorySerializer(historys, many=True)
        return Response(serializer.data)
    def post(self, request):
        """
        添加搜索历史
        """
        # /history/
        # user = request.user
        user_id = 1
        serializer = PcSearchHistorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pc_id = serializer.validated_data.get('pc_id')
        name = serializer.validated_data.get('name')
        image_url = serializer.validated_data.get('image_url')
        """
            history_userid = [
         {
        1:{
            "image_url": "wwww,ss",
            "name": "sss"
        },
        2: {
            "image_url": "wwww,ss",
                    "name": "sss"
        }
    }
] 
        """

        """
                   history_userid = [
           {        "pc_id":pc_id
                   "image_url": "wwww,ss",
                   "name": "sss"
               },
                    "pc_id": pc_id
                   "image_url": "wwww,ss",
                           "name": "sss"              
           }
           
       ] 
       {
"pc_id":2,
"image_url":"wwer",
'name":"sdasd"
}
               """

        print(pc_id)
        # 使用pickle序列化数据，pickle操作的是bytes类型
        historys = request.COOKIES.get('history_%s' % user_id)
        print(historys)
        print(type(historys))
        if historys is not None:
            historys = pickle.loads(base64.b64decode(historys.encode()))
            historys_list = historys[::]
            # 先删除cookies中存在的搜索历史，目的在于去重
            for i in historys_list:
                if pc_id == i["pc_id"]:
                    historys.remove(i)
                    print(i["pc_id"])
            # 插入数据，保持顺序
            historys.insert(0, {"pc_id": pc_id, "image_url": image_url, "name": name})
            if len(historys) > constants.HISTORY_COOKIES_COUNTS_LIMIT:
                historys = historys[:constants.HISTORY_COOKIES_COUNTS_LIMI]
            print(historys)
        # 以上条件不成立，则搜索历史为空
        else:
            historys = []

            historys.insert(0, {"pc_id": pc_id, "image_url":image_url, "name": name})
        historys = base64.b64encode(pickle.dumps(historys)).decode()

        # cookie_cart = base64.b64encode(pickle.dumps(history)).decode()

        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        # 设置搜索历史的cookie
        # 需要设置有效期，否则是临时cookie
        response.set_cookie('history_%s' % user_id, historys, max_age=constants.CART_COOKIE_EXPIRES)

        return response


# -----------------清空搜索历史（cookies）---------------
class HistoryClearAPIView(APIView):
    # 这里用get方法代替delete方法，前端人员要求
    # /history/clear
    def get(self, request):
        """
        删除采集搜索历史
        """
        user_id = 1
        # try:
        #     user = request.user
        # except Exception:
        #
        #     user = None
        historys = request.COOKIES.get("history_%s" % user_id)
        response = Response({"message":"删除成功"}, status=status.HTTP_204_NO_CONTENT)
        if historys is not None:
            response.delete_cookie("history_%s" % user_id)
        return response


#------------------添加采集任务-----------------

class TaskaddAPIView(APIView):
    """
    添加采集任务
    """

    # def post(self, request):
    def post(self, request):
        """
        添加采集任务
        """

        # {
        #   "pc_id": 2,
        # "collect_type":["colloct_type","ss"],
        # "selected": "True"
        # }

        serializer = TaskSerializer(data=request.data)
        print(1111)
        serializer.is_valid(raise_exception=True)
        pc_id = serializer.validated_data.get('pc_id')
        collect_type = serializer.validated_data.get('collect_type')
        selected = serializer.validated_data.get('selected')
        # user = request.user
        # 数据类型 "2018-10-2","2019-10-20"
        id = 1
        # 获取当前公众号信息
        # pc_id = 1
        # collect_type = ["2018-09-10", "2019-11-10"]
        # selected = True
        pc = PublicNum.objects.get(id=pc_id)

        # 尝试对请求的用户所选采集方式进行验证
        if len(collect_type) == 1:
            print(collect_type)
            try:
                int(collect_type[0])
            except ValueError:
                ls = collect_type[0].split(",")
                cl_date_start = ls[0]
                cl_date_end = ls[1]
                article_total_count = 0
            else:
                article_total_count = collect_type[0]
                cl_date_end = None
                cl_date_start = None

        CollectTask.objects.create(name=pc.name, article_total_count=article_total_count,_biz=pc._biz,cl_date_start=cl_date_start,
                                   cl_date_end=cl_date_end, public_id=pc_id, user_id=id, rl_count=selected)

        # 把保存redis的pc_id在list中删除
        # redis_conn = get_redis_connection("collect_list")
        #
        # redis_conn.lrem("collect_%s" % id, 0, pc_id)

        return Response({"message":"ok"}, status=status.HTTP_201_CREATED)

# -----------------查看采集任务------------------
class TasklistAPIView(ListAPIView):


#  GET /tasks/list/
    serializer_class = CollectTaskSerializer
    pagination_class = None
    def get_queryset(self):
        # user = self.request.user
        user = 1
        query_set = CollectTask.objects.filter(task_status=CollectTask.TASK_STATUS_ENUM["CATCHED"],user_id=1)
        return query_set

# ------------------查看任务详情页-------------------

class TaskShowDetailAPIView(APIView):

    # /tasks/detail?task_id=xxxx
    def get(self, request):
        # user = request.user
        # 从任务表中查看抓取完成的公众号id
        task_id = request.query_params.get("task_id")
        obj = CollectTask.objects.filter(task_status=CollectTask.TASK_STATUS_ENUM["CATCHED"], user_id=1, id = task_id).first()
        # 获取任务表中，读赞数的勾选状态
        selected = obj.rl_count
        print(obj)
        # 获取文章任务表中文章总数
        at_count = obj.article_total_count
        # print(at_count)
        # 根据公众号id查询对应的公众号表
        pc = PublicNum.objects.get(id=obj.public_id)
        # print(pc)
        # 根据公众号去查询对应的文章数
        at = pc.article_set.order_by('id')[:at_count]
        # 如果任务列表中读赞数有勾选，则返回读赞数
        if selected:
            # 获取文章平均点赞数、平均阅读数
            at_like_avg = at.aggregate(Avg('like_numbers'))["like_numbers__avg"]
            # print(at_like_avg)
            at_read_avg = at.aggregate(Avg('read_numbers'))["read_numbers__avg"]
            # print(at_like_avg)
            # 返回数据给前端
        else:
            at_like_avg = 0
            at_read_avg = 0

        data = {
            "name": pc.name,
            "at_like_avg": at_like_avg,
            "at_read_avg": at_read_avg,
            "at_count": at_count,
            "task_status": obj.task_status
        }
        serializer = TaskShowDetailSerializer(data)

        return Response(serializer.data)
class TaskdeleteAPIView(APIView):

    def get(self, request):
        task_id = request.query_params.get("task_id")
        # / tasks/delete?task_id=xxxx
        # 查看要删除的任务
        obj = CollectTask.objects.filter(task_status=CollectTask.TASK_STATUS_ENUM["CATCHED"], user_id=1,
                                         id=task_id).first()

        # 删除相应任务
        obj.delete()
        return Response({"message": "删除任务成功"}, status=status.HTTP_204_NO_CONTENT)


# -----------------查看任务文章页-----------------
class ArticleShowDetailAPIView(APIView):
    """
    文章详情页
    """
    # permission_classes = [IsAuthenticated]
    # /arts/(?P<task_id>\d+)/list
    def get(self, request):
        """
        获取
        """
        # user = request.user
        task_id = request.query_params.get("task_id")
        user_id = 1
        # 查询任务表根据公众号和用ｉｄ找到相应的微信公众号ｉｄ
        task = CollectTask.objects.filter(user_id=user_id, id=task_id).first()

        pc = PublicNum.objects.get(id=task.public_id)
        # 根据公众号查询所有文章
        arts = pc.article_set.all()
        print(arts)
        # 图片默认url
        image_url = pc.image_url
        print(image_url)

        serializer = ArticleShowDetailSerializer({'image_url': image_url, 'arts': arts})
        return Response(serializer.data)

# -----------------文章下载--------------

