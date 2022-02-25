from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from blog.api.v1.permissions import IsUserOwner
from blog.api.v1.serializers import AdSerializer
from blog.models import Ad


class ListCreateAdView(ListCreateAPIView):
    queryset = Ad.objects.filter(moderated=True)
    serializer_class = AdSerializer
    pagination_class = PageNumberPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    # def get(self, request, *args, **kwargs):
    #     ads = Ad.objects.filter(moderated=False).values('id', 'title')
    #     return Response(ads)

    @method_decorator(login_required())
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AdSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data)


class RetrieveUpdateDestroyAdView(RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserOwner]

    # def put(self, request, *args, **kwargs):
    #     data = self.request.data
    #     pk = self.kwargs.get('pk')
    #     if pk:
    #         instance = get_object_or_404(Ad, id=pk)
    #         price = data.get('price')
    #         if price is not None and int(price) > 0 and instance.user == request.user:
    #             instance.price = data.get('price')
    #             instance.title = data.get('title')
    #             instance.save()
    #             return Response(AdSerializer(instance).data)
    #         else:
    #             return JsonResponse({"error": 'price can not be negative'}, status=HTTP_404_NOT_FOUND)
    #     else:
    #         return JsonResponse({"sad": 'object does not exists'})


@api_view(['GET', 'POST'])
def get_list_ads(request, *args, **kwargs):
    ads = Ad.objects.all()
    serializer = AdSerializer(ads, many=True)
    if request.method == 'POST':
        data = request.data
        serializer = AdSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    return Response({'ads': serializer.data})

