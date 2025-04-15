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
from rest_framework import permissions
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .throttles import TenCallsPerMinute  # import your throttle

#view to render menu items
class MenuItemListView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow everyone to access this view
    throttle_classes = [TenCallsPerMinute]

    def get(self, request):
        items = MenuItem.objects.all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', 10)
        page = request.query_params.get('page', 1)

        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(page)
        except EmptyPage:
            items = []


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
    throttle_classes = [TenCallsPerMinute]

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
        if request.user.groups.filter(name='Managers').exists() or request.user.is_superuser:
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
        if request.user.groups.filter(name='Managers').exists() or request.user.is_superuser:
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
        if request.user.groups.filter(name='Managers').exists() or request.user.is_superuser:
            try:
                item = MenuItem.objects.get(pk=pk)  # Get the item to delete
            except MenuItem.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            item.delete()  # Delete the item
            return Response({"message": "Item deleted successfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)



# View to create categories
class CreateCategory(APIView):
    throttle_classes = [TenCallsPerMinute]
    permission_classes = [IsAdminUser] # checks if the user is admin
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data,status.HTTP_201_CREATED )



# View to render categories
class CategoryListView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view
    throttle_classes = [TenCallsPerMinute]

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
    throttle_classes = [TenCallsPerMinute]

    def get(self, request):
        user = request.user  # Get the current logged-in user

        if not (user.groups.filter(name="Managers").exists() or user.is_superuser): # Check if the user is either a superuser (admin) or belongs to the 'Manager' group
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

        if not (user.groups.filter(name="Managers").exists() or user.is_superuser):  # Only allow superusers or managers to add users to the group
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
    throttle_classes = [TenCallsPerMinute]

    def get(self, request):
        # Restrict GET to Manager or Admin only
        if not (request.user.groups.filter(name='Managers').exists() or request.user.is_superuser):
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
    throttle_classes = [TenCallsPerMinute]

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
    throttle_classes = [TenCallsPerMinute]

    def get(self, request):
        user = request.user

        if user.groups.filter(name="Managers").exists() or user.is_superuser:
            # Managers can see all orders (with or without delivery crew)
            orders = Order.objects.all().order_by('-date')

        elif user.groups.filter(name="Delivery Crew").exists():
            # Delivery crews can only see orders assigned to them
            orders = Order.objects.filter(delivery_crew=user).order_by('-date')

        else:
            # Customers (non-Manager and non-DeliveryCrew) can only see their own orders
            orders = Order.objects.filter(user=user).order_by('-date')

        # Serialize the orders and return them
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


    def put(self, request, pk):
        # Ensure that the user is a Manager or Admin
        if not (request.user.groups.filter(name='Managers').exists() or request.user.is_superuser):
            return Response({"detail": "You do not have permission to edit this order."}, status=status.HTTP_403_FORBIDDEN)

        # Try to get the order from the database
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get the delivery crew user ID from the request data (if any)
        delivery_crew_id = request.data.get('Delivery Crew')

        # If a delivery crew ID is provided, assign the user to the order
        if delivery_crew_id:
            try:
                delivery_crew = User.objects.get(pk=delivery_crew_id)
                # Ensure the selected user is in the 'DeliveryCrew' group
                if not delivery_crew.groups.filter(name="Delivery Crew").exists():
                    return Response({"error": "The selected user is not in the Delivery Crew group."}, status=status.HTTP_400_BAD_REQUEST)

                order.delivery_crew = delivery_crew  # Assign the delivery crew to the order

            except User.DoesNotExist:
                return Response({"detail": "The specified delivery crew user does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Update order with any other fields in the request data
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated order
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If serializer validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        user = request.user

        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # === MANAGER / ADMIN ===
        if user.groups.filter(name='Managers').exists() or user.is_superuser:
            # Managers can update any field partially
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # === DELIVERY CREW ===
        elif user.groups.filter(name='Delivery Crew').exists():
            # Delivery Crew can only update 'status' on their assigned orders
            if order.delivery_crew != user:
                return Response({"detail": "This order is not assigned to you."}, status=status.HTTP_403_FORBIDDEN)

            # Only 'status' field should be allowed
            if 'status' not in request.data:
                return Response({"detail": "Missing 'status' field."}, status=status.HTTP_400_BAD_REQUEST)

            # Must not try to update other fields
            if set(request.data.keys()) != {'status'}:
                return Response({"detail": "You can only update the 'status' field."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the value of status
            status_value = request.data['status']
            if status_value not in [0, 1, True, False]:
                return Response({"detail": "Status must be 0 or 1."}, status=status.HTTP_400_BAD_REQUEST)

            # Update and save
            order.status = bool(status_value)
            order.save()
            return Response({"detail": "Order status updated."}, status=status.HTTP_200_OK)

        # === CUSTOMERS ===
        else:
            return Response({"detail": "You do not have permission to edit this order."}, status=status.HTTP_403_FORBIDDEN)



    def delete(self, request, pk):
        if not (request.user.groups.filter(name='Managers').exists() or request.user.is_superuser): # Restrict DELETE access to Manager or Admin only
            return Response({"detail": "You do not have permission to edit this order."}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(pk=pk)  # Get the order to delete
            order.delete()  # Delete the order
            return Response({"message": "Order successfully deleted"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)





# retrieves order
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [TenCallsPerMinute]

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


