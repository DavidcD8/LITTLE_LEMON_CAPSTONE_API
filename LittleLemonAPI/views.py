from datetime import date
from django.shortcuts import render,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import generics
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from .models import MenuItem
from .serializers import MenuItemSerializer, CategorySerializer,CartSerializer, OrderSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission
from rest_framework import permissions



#view to render menu items
class MenuItemListView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow everyone to access this view

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
        # Restrict POST to Manager or Admin only
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)





# Renders one item only and acceps put and patch
class SingleMenuItemView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow access without authentication for GET

    def get(self, request, pk):
        try:
            item = MenuItem.objects.get(pk=pk)  # Get the item by primary key
        except MenuItem.DoesNotExist:
            return Response({'message': "The item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        # Restrict PUT access to Manager or Admin only
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            try:
                item = MenuItem.objects.get(pk=pk)  # Get the item to update
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()  # Save the updated item
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk):
        # Restrict PATCH access to Manager or Admin only
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            try:
                item = MenuItem.objects.get(pk=pk)  # Get the item to update
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(item, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()  # Save the updated item
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        # Restrict DELETE access to Manager or Admin only
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            try:
                item = MenuItem.objects.get(pk=pk)  # Get the item to delete
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            item.delete()  # Delete the item
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
    permission_classes = [IsAuthenticated] # Only allow authenticated users to access this view


    def get(self, request):
        user = request.user  # Get the current logged-in user

        if not (user.groups.filter(name="Manager").exists() or user.is_superuser): # Check if the user is either a superuser (admin) or belongs to the 'Manager' group
            return Response({"detail": "You do not have permission to view this."}, status=status.HTTP_403_FORBIDDEN)  # If not authorized, return 403 Forbidden
        try:
            manager_group = Group.objects.get(name="Managers")  # Try to get the 'Managers' group
        except Group.DoesNotExist:
            return Response({"message": "Managers group does not exist"}, status=status.HTTP_404_NOT_FOUND) # If it doesn't exist, return 404 Not Found
        managers = manager_group.user_set.all() # Get all users in the 'Managers' group
        manager_data = [{"id": user.id, "username": user.username} for user in managers]# Create a list of dictionaries with each manager's ID and username
        return Response({'managers': manager_data}) # Return the list of managers in the response


    def post(self, request):
        user = request.user  # Get the current logged-in user

        if not (user.groups.filter(name="Manager").exists() or user.is_superuser):  # Only allow superusers or managers to add users to the group
            return Response({"detail": "You do not have permission to add users."}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get("user_id")  # Extract the user_id from the request body
        if not user_id:
            return Response({"detail": "Missing 'user_id' in payload."}, status=status.HTTP_400_BAD_REQUEST) # If no user_id is provided, return 400 Bad Request
        try:
            target_user = User.objects.get(id=user_id)# Try to get the user to be added
            manager_group = Group.objects.get(name="Managers") # Try to get the 'Managers' group
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)   # If the user does not exist, return 404
        except Group.DoesNotExist:
            return Response({"detail": "Managers group does not exist."}, status=status.HTTP_404_NOT_FOUND)  # If the group does not exist, return 404
        if target_user.groups.filter(name="Managers").exists():        # Check if the user is already in the group
            return Response({"message": "User is already in the Managers group."}, status=status.HTTP_200_OK) # If so, return a message saying no action is needed
        target_user.groups.add(manager_group) # Add the user to the Managers group
        return Response({"message": "User added to Managers group."}, status=status.HTTP_201_CREATED)        # Return success message with 201 Created status


    def delete(self, request, user_id=None):
        user = request.user  # Get the current logged-in user

        if not (user.groups.filter(name="Manager").exists() or user.is_superuser): # Only allow superusers or managers to remove users from the group
            return Response({"detail": "You do not have permission to remove users."}, status=status.HTTP_403_FORBIDDEN)
        if not user_id:
            return Response({"detail": "Missing user_id in URL."}, status=status.HTTP_400_BAD_REQUEST) # If no user_id is provided in the URL, return 400 Bad Request
        try:
            target_user = User.objects.get(id=user_id)  # Try to get the user to be removed
            manager_group = Group.objects.get(name="Managers") # Try to get the 'Managers' group
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND) # If the user does not exist, return 404
        except Group.DoesNotExist:
            return Response({"detail": "Managers group does not exist."}, status=status.HTTP_404_NOT_FOUND) # If the group does not exist, return 404
        if target_user.groups.filter(name="Managers").exists():# Check if the user is in the group
            target_user.groups.remove(manager_group)# Remove the user from the group
            return Response({"message": "User removed from Managers group."}, status=status.HTTP_200_OK) # Return success message
        return Response({"message": "User not in Managers group."}, status=status.HTTP_404_NOT_FOUND) # If the user was not in the group, return a 404 message









# view to add user to delivery group by manager or admin
class AssignDeliveryView(APIView):
    def get(self, request):
        # Restrict GET to Manager or Admin only
        if not (request.user.groups.filter(name='Manager').exists() or request.user.is_superuser):
            return Response({"detail": "You do not have permission to view this."}, status=status.HTTP_403_FORBIDDEN)

        try:
            delivery_group = Group.objects.get(name="Delivery Crew")  # Get the Delivery group
        except Group.DoesNotExist:
            return Response({"message": "Delivery Crew does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Get all users in the Delivery group
        delivery = delivery_group.user_set.all()

        # Create a list of users with the data you want to return
        delivery_data = [{"id": user.id, "username": user.username} for user in delivery]

        return Response({'delivery': delivery_data})

    def post(self, request, user_id=None):
        # Restrict POST to Manager or Admin only
        if not (request.user.groups.filter(name='Managers').exists() or request.user.is_superuser):
            return Response({"detail": "You do not have permission to add users."}, status=status.HTTP_403_FORBIDDEN)

        if not user_id:
            return Response({"detail": "Missing 'user_id' in URL."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)  # Get the user by ID
            delivery_group = Group.objects.get(name="Delivery Crew")  # Get the Delivery Crew group
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Delivery group does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Delivery Crew").exists():  # Check if the user is already in the Delivery Crew
            return Response({"message": "User is already in the Delivery Crew."}, status=status.HTTP_200_OK)

        user.groups.add(delivery_group)  # Add the user to the Delivery Crew group
        return Response({"message": "User added to Delivery group."}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id=None):
        # Restrict DELETE to Manager or Admin only
        if not (request.user.groups.filter(name='Managers').exists() or request.user.is_superuser):
            return Response({"detail": "You do not have permission to remove users."}, status=status.HTTP_403_FORBIDDEN)

        if not user_id:
            return Response({"detail": "Missing 'user_id' in URL."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)  # Get the user by ID
            delivery_group = Group.objects.get(name="Delivery Crew")  # Get the Delivery Crew group
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Delivery Crew does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Delivery Crew").exists():  # Check if user is in the Delivery Crew group
            user.groups.remove(delivery_group)  # Remove the user from the group
            return Response({"message": "User removed from Delivery Crew."}, status=status.HTTP_200_OK)

        return Response({"message": "User not in Delivery Crew."}, status=status.HTTP_404_NOT_FOUND)  # User was not in the group


# Cart view
class CartView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Retrieves authentcated user from the token
        cart_items = Cart.objects.filter(user=user)  # Fetch cart items for the authenticated user
        serialized = CartSerializer(cart_items, many=True)  # Serialize the cart items
        return Response(serialized.data, status=status.HTTP_200_OK)  # Return serialized data with 200 status


    def post(self, request):
        serializer = CartSerializer(data=request.data, context={'request': request})  # Inject user into serializer context
        if serializer.is_valid():  # Check if the data is valid
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return serialized data with 201 status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors with 400 status


    def delete(self, request, item_id):
        try:
            item = Cart.objects.get(user=request.user, menuitem_id=item_id)
            item.delete()
            return Response({"message": "Item successfully deleted"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)



# Order view
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if user is Manager or Admin using built-in permissions
        if user.groups.filter(name='Manager').exists() or user.is_superuser:
            orders = Order.objects.all().order_by('-date')
        else:
            orders = Order.objects.filter(user=user).order_by('-date')

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def post(self, request):
        user = request.user  # Retrieves authenticated user from the token
        cart_items = Cart.objects.filter(user=user)  # Only fetch the items belonging to the authenticated user.

        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=400)  # Check if the cart is empty and returns error if there are no items in the cart

        total = 0  # This will accumulate the total price of the order as we iterate through the cart items.

        # Create the order and set the current date
        order = Order.objects.create(
            user=user,
            total=0,  # Initially set to 0; will be updated later
            date=date.today()  # Set the date to today
        )

        for item in cart_items:
            item_total = item.menuitem.price * item.quantity  # Calculates the total price for the item

            # Create an OrderItem for each cart item, which is linked to the Order
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.menuitem.price,
                price=item_total
            )

            total += item_total  # Update the total with the item price

        # Update the order's total price
        order.total = total
        order.save()

        # Clear the cart after successfully placing the order
        cart_items.delete()

        return Response({"message": "Order placed", "order_id": order.id}, status=201)


# retrieves order
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.user != request.user:
            return Response({"error": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)

        order_items = OrderItem.objects.filter(order=order)
        data = {
            "order_id": order.id,
            "total": order.total,
            "date": order.date,
            "items": [
                {
                    "menuitem": item.menuitem.title,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "price": item.price,
                }
                for item in order_items
            ]
        }
        return Response(data, status=status.HTTP_200_OK)