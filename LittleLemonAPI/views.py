from django.shortcuts import render,get_object_or_404
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import generics
from rest_framework.views import APIView, Response, status
from .models import MenuItem
from .serializers import MenuItemSerializer
 

class CreateMenuItemView(APIView):
    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
 

class MenuItemList(APIView):
    def get(self, request):
        menu_items = MenuItem.objects.all()  # Fetch all menu items
        if menu_items.exists():  # Check if there are any items
            serializer = MenuItemSerializer(menu_items, many=True)
            return Response(serializer.data, status.HTTP_200_OK)  # Return the serialized data with 200 status
        else:
            return Response({"detail": "No menu items found."}, status.HTTP_404_NOT_FOUND)  # If no items found, return 404

 