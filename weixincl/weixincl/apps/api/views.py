from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response


from api.models import ParamPass
from api.serializers import PassParamsSerializer, SavePcSerializer


class PassParamsAPIView(ListAPIView):
    serializer_class = PassParamsSerializer
    pagination_class = None

    def get_queryset(self):
        query_set = ParamPass.objects.all()
        return query_set

class SavePcCreateView(CreateAPIView):
    """
    保存微信公众号
    """

    # permission_classes = [IsAuthenticated]
    serializer_class = SavePcSerializer




