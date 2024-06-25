from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins, status

from foods.serializers import FoodSerializer
from .models import Pet
from .serializers import PetSerializer, PetCreateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .recommendations import recommend_food


class PetListCreateView(generics.ListCreateAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    @swagger_auto_schema(responses={200: PetSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=PetCreateSerializer, responses={201: PetSerializer})
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class PetRetrieveView(generics.RetrieveAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    @swagger_auto_schema(responses={200: PetSerializer})
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class PetUpdateView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    @swagger_auto_schema(request_body=PetSerializer, responses={200: PetSerializer})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class PetDeleteView(mixins.DestroyModelMixin, generics.RetrieveAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    @swagger_auto_schema(responses={204: 'No content'})
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class PetCreateView(APIView):
    @swagger_auto_schema(request_body=PetCreateSerializer, responses={201: PetSerializer})
    def post(self, request, format=None):
        serializer = PetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PetFeedView(APIView):
    def get(self, request):
        serializer = PetSerializer(data=request.query_params)
        if serializer.is_valid():
            pet = Pet.objects.get(id=serializer.validated_data['pet_id'])
            recommended_food_name, recommended_amount, min_nutrients = recommend_food(pet)
            data = {
                'recommended_food_name': recommended_food_name,
                'recommended_amount': recommended_amount,
                'min_nutrients': min_nutrients,
            }
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
