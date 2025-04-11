from django.shortcuts import render,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import generics
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import MenuItem
from .serializers import MenuItemSerializer, CategorySerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission


#view to create menu items
class CreateMenuItemView(APIView):
    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#view to render menu items
class MenuItemList(APIView):
    permission_classes = [IsAdminUser] # checks if the user is admin
    def get(self, request):
        menu_items = MenuItem.objects.all()  # Fetch all menu items
        if menu_items.exists():  # Check if there are any items
            serializer = MenuItemSerializer(menu_items, many=True)
            return Response(serializer.data, status.HTTP_200_OK)  # Return the serialized data with 200 status
        else:
            return Response({"detail": "No menu items found."}, status=status.HTTP_404_NOT_FOUND)


# View to create categories
class CreateCategory(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser] # checks if the user is admin
    queryset =  Category.objects.all() # Fetch all categories
    serializer_class = CategorySerializer


# View to render categories
class CategoryListView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get(self, request):
        categories = Category.objects.all()  # Fetch all categories
        if categories.exists():  # Check if there are any categories
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return serialized data with 200 status
        else:
            return Response({"detail": "No categories found."}, status=status.HTTP_404_NOT_FOUND)  # Adjust error message for categories


# view to add user to Managers group
class AssignGroupView(APIView):
    permission_classes = [IsAdminUser]  # Checks if the user is an admin

    def post(self, request):
        try:
            # Get the 'Managers' group from your database
            manager_group = Group.objects.get(name='Managers')
        except ObjectDoesNotExist:
            # If the group doesn't exist, return a 404 error
            return Response({'message': "Managers group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already in the 'Managers' group
        if request.user.groups.filter(name='Managers').exists():
            return Response({'message': "User is already in the managers group"}, status=status.HTTP_200_OK)

        # Add the user to the 'Managers' group if they are not already in it
        request.user.groups.add(manager_group)
        return Response({'message': "User added to managers group"}, status=status.HTTP_201_CREATED) 



# view to remove user from Managers group
class RemoveGroupView(APIView):
    permission_classes = [IsAdminUser]  # Checks if the user is an admin

    def post(self, request):
        try:
            # Get the 'Managers' group
            manager_group = Group.objects.get(name='Managers')
        except ObjectDoesNotExist:
            return Response({'message': "Managers group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is in the 'Managers' group
        if request.user.groups.filter(name='Managers').exists():
            # Remove the user from the 'Managers' group
            request.user.groups.remove(manager_group)
            return Response({'message': "User removed from managers group"}, status=status.HTTP_200_OK)

        # If the user is not in the 'Managers' group
        return Response({'message': "User not found in the managers group"}, status=status.HTTP_404_NOT_FOUND)



# Custom permission to check if the user is in the 'Managers' group.
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Managers').exists()



# view to add user to delivery group by manager
class AssignDeliveryView(APIView):
    permission_classes = [IsManager] # Checks if the user is an manager

    def post(self, request):
        try:
            # Get the 'Delivery Crew' group
            delivery_group = Group.objects.get(name='Delivery Crew')
        except ObjectDoesNotExist:
            return Response({'message': "Delivery group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already in the 'Delivery Crew' group
        if request.user.groups.filter(name='Delivery Crew').exists():
            return Response({'message': "User is already in the Delivery Crew group"}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the 'Delivery Crew' group
        request.user.groups.add(delivery_group)

        # Return a success response
        return Response({'message': "User successfully added to the Delivery Crew group"}, status=status.HTTP_200_OK)



# view to remove user from delivery group
class RemoveDeliveryView(APIView):
    permission_classes = [IsManager]  # Checks if the user is an manager

    def post(self, request):
        try:
            # Get the 'Delivery' group
            delivery_group = Group.objects.get(name='Delivery Crew')
        except ObjectDoesNotExist:
            return Response({'message': "Delivery group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is in the 'Delivery' group
        if request.user.groups.filter(name='Delivery Crew').exists():
            # Remove the user from the 'Delivery' group
            request.user.groups.remove(delivery_group)
            return Response({'message': "User removed from Delivery group"}, status=status.HTTP_200_OK)

        # If the user is not in the 'Delivery' group
        return Response({'message': "User not found in the Delivery group"}, status=status.HTTP_404_NOT_FOUND)

