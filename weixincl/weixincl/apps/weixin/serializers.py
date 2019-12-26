from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.views import APIView

from weixin import constants
from weixin.models import PublicNum, CollectTask, Article

# 宫中号系列化器
class PcNumSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicNum
        fields = ["id", "name", "image_url", "_biz", "introduction", "weixin_num"]


class AddCollectListSerializer(serializers.Serializer):
    """采集列表的序列化器"""
    pc_id = serializers.IntegerField(label="公众号编号", min_value=1)

    def validate_pc_id(self, value):
        """
        检验公众号pc_id是否存在
        """
        # print(111)
        try:
            PublicNum.objects.get(id=value)
        except PublicNum.DoesNotExist:
            raise serializers.ValidationError('该公众号不存在')
        return value
    # def validate_image_url(self, value):
    #     value = "http//192.168.81.128:8001" + value
    #     print(value)
    #     return value

    def create(self, validated_data):
        # 获取当前登陆的用户id
        # user_id = self.context['request'].user.id
        user_id = 1
        pc_id = validated_data['pc_id']
        """redis中保存历史记录的数据类型格式

        例如，本次用户访问的pc_id是2,

        user_id: [
           7,6,1,4,2
        ]
        """
        # 把sku_id保存redis的list类型数据中
        redis_conn = get_redis_connection("collect_list")
        pl = redis_conn.pipeline()
        # 删除redis中同样的sku_id,
        pl.lrem("collect_%s" % user_id, 0, pc_id)
        # 然后添加sku_id到redis
        pl.lpush("collect_%s" % user_id, pc_id)
        # 如果超过最大长度，则最后一个成员要被剔除
        pl.ltrim("collect_%s" % user_id, 0, constants.USER_COLLECT_HISTORY_COUNTS_LIMIT - 1)
        pl.execute()

        return validated_data


# 添加采集任务系列
class TaskSerializer(serializers.Serializer):
    """
    任务创建序列化器
    """
    pc_id = serializers.IntegerField(label='pc id ', min_value=1)
    # 校验采集列表
    collect_type = serializers.ListField(label='采集类型', allow_empty=False, max_length=10)
    selected = serializers.BooleanField(label='是否勾选', default=True)

# 查看采集任务系列器
class CollectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectTask
        fields = ["id", "name", "task_status", "article_total_count", "task_time", "public", "user", "rl_count"]


# 查看任务详情页系列化器
class TaskShowDetailSerializer(serializers.Serializer):
    name = serializers.CharField(label="公众号名称", max_length=10)
    at_like_avg = serializers.IntegerField(label="平均点赞数", min_value=2)
    at_read_avg = serializers.IntegerField(label="平均点赞数", min_value=2)
    at_count = serializers.IntegerField(label="文章总数", min_value=2)
    task_status = serializers.IntegerField(label="任务状态", min_value=1)
# 文章表系列化器
class ArticleSerializer(serializers.ModelSerializer):
    """
    文章数据序列化器
    """
    # count = serializers.IntegerField(label='数量')

    class Meta:
        model = Article
        fields = ('id', 'publish_time', 'collect_time', 'title', 'author', 'html_text',
                  'like_numbers', 'content', 'read_numbers')


class ArticleShowDetailSerializer(serializers.Serializer):
    """
    文章详情数据序列化器
    """
    image_url = serializers.CharField(label='默认图片', max_length=50)
    arts = ArticleSerializer(many=True)

class PcSearchHistorySerializer(serializers.Serializer):
    pc_id = serializers.IntegerField(label="微信公众号id", min_value=1)
    image_url = serializers.CharField(label='默认图片', max_length=100)
    name = serializers.CharField(label='公众号名称', max_length=20)
