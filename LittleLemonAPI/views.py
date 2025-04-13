from django.shortcuts import render,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import generics
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import MenuItem
from .serializers import MenuItemSerializer, CategorySerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission



# view to prevent unwanted actions
class DenyUnsafeMethodsMixin:
    def post(self, request, *args, **kwargs):
        return self.permission_denied_response()

    def put(self, request, *args, **kwargs):
        return self.permission_denied_response()

    def patch(self, request, *args, **kwargs):
        return self.permission_denied_response()

    def delete(self, request, *args, **kwargs):
        return self.permission_denied_response()

    def permission_denied_response(self):
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )


# Custom permission to check if the user is in the 'Managers' group.
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Managers').exists()



#view to render menu items
class MenuItemListView(APIView,DenyUnsafeMethodsMixin):
    permission_classes = [AllowAny]  # Allow everyone to access this view

    def get(self, request):
        items = MenuItem.objects.all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')

        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)

        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        if IsManager().has_permission(request, self) or IsAdminUser().has_permission(request, self):
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)



# Renders one item only and acceps put and patch
class SingleMenuItemView(APIView,DenyUnsafeMethodsMixin):
    permission_classes = [AllowAny]  # Allow access without authentication

    def get(self, request, pk):
        try:
            item = MenuItem.objects.get(pk=pk) # Get the item
        except ObjectDoesNotExist:
            return Response({'message': "The item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')

        if category_name:
            item = item.filter(category__title=category_name)
        if to_price:
            item = item.filter(price__lte=to_price)
        if search:
            item = item.filter(title__icontains=search)

        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request, pk): # only managers and amin can use this
        if IsManager().has_permission(request, self) or IsAdminUser().has_permission(request, self):
            try:
                item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


    def patch(self, request, pk): # only managers and amin can use this
        if IsManager().has_permission(request, self) or IsAdminUser().has_permission(request, self):
            try:
                item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


    def delete(self, request, pk): # this method deleted an object from menu
        if IsManager().has_permission(request, self) or IsAdminUser().has_permission(request, self):
            try:
                item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            item.delete()
            return Response({"message": "Item deleted successfully."}, status=status.HTTP_200_OK)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)



# View to create categories
class CreateCategory(APIView):
    permission_classes = [IsAdminUser] # checks if the user is admin
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data,status.HTTP_201_CREATED )



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
class ManagerGroupView(APIView):
    permission_classes = [IsAdminUser | IsManager]

    def get(self, request):
        try:
            # Get the Managers group
            manager_group = Group.objects.get(name="Managers")
        except Group.DoesNotExist:
            return Response({"message": "Managers group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Get all users in the 'Managers' group
        managers = manager_group.user_set.all()

        # Create a list of users with the data you want to return
        manager_data = [{"id": user.id, "username": user.username} for user in managers]

        return Response({'managers': manager_data})


    def post(self, request):
        user_id = request.data.get("user_id") # Gets the user ID from the request payload
        if not user_id:
            return Response({"detail": "Missing 'user_id' in payload."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id) # Gets the user ID from the request payload
            manager_group = Group.objects.get(name="Managers") # Retrieves the Group object with the name Managers from the database

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Managers group does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Managers").exists(): # Check if the user is in the Managers group
            return Response({"message": "User is already in the Managers group."}, status=status.HTTP_200_OK)

        user.groups.add(manager_group)
        return Response({"message": "User added to Managers group."}, status=status.HTTP_201_CREATED)


    def delete(self, request, user_id=None):
        if not user_id:
            return Response({"detail": "Missing user_id in URL."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id) # Gets the user ID from the request payload
            manager_group = Group.objects.get(name="Managers") # Retrieves the Group object with the name Managers from the database

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Managers group does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Managers").exists(): # Check if the user is in the Managers group
            user.groups.remove(manager_group)
            return Response({"message": "User removed from Managers group."}, status=status.HTTP_200_OK)

        return Response({"message": "User not in Managers group."}, status=status.HTTP_404_NOT_FOUND)







# view to add user to delivery group by manager or admin
class AssignDeliveryView(APIView):
    permission_classes = [IsAdminUser | IsManager]

    def get(self, request):
        try:
            delivery_group = Group.objects.get(name="Delivery Crew") # Get the Delivery group
        except Group.DoesNotExist:
            return Response({"message": "Delivery Crew does not exist"}, status=404)

        # Get all users in the Delivery group
        delivery = delivery_group.user_set.all()

        # Create a list of users with the data you want to return
        delivery_data = [{"id": user.id, "username": user.username} for user in delivery]

        return Response({'delivery': delivery_data})


    def post(self, request):
        user_id = request.data.get("user_id") # Gets the user ID from the request payload
        if not user_id:
            return Response({"detail": "Missing 'user_id' in payload."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id) # Gets the user ID from the request payload
            delivery_group = Group.objects.get(name="Delivery Crew") # Retrieves the Group object with the name Delivery Crew from the database

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Delivery group does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Delivery Crew").exists(): # Check if the user is in the Delivery group
            return Response({"message": "User is already in the Delivery Crew."}, status=status.HTTP_200_OK)

        user.groups.add(delivery_group)
        return Response({"message": "User added to Delivery group."}, status=status.HTTP_201_CREATED)


    def delete(self, request, user_id=None):
        if not user_id:
            return Response({"detail": "Missing user_id in URL."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id) # Gets the user ID from the request payload
            delivery_group = Group.objects.get(name="Delivery Crew") # Retrieves the Group object with the name Delivery Crew from the database

        except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Delivery Crew does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if user.groups.filter(name="Delivery Crew").exists(): # Checks if the user is in the Delivery Crew
            user.groups.remove(delivery_group)
            return Response({"message": "User removed from Delivery Crew."}, status=status.HTTP_200_OK)

        return Response({"message": "User not in Delivery Crew."}, status=status.HTTP_404_NOT_FOUND)