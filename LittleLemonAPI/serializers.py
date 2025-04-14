from rest_framework import serializers
from .models import MenuItem , Category, Cart

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['user', 'unit_price', 'price']

    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']

        # Check if cart item already exists
        existing_cart_item = Cart.objects.filter(user=user, menuitem=menuitem).first()

        if existing_cart_item:
            # If it exists, update the quantity and prices
            existing_cart_item.quantity += quantity
            existing_cart_item.unit_price = menuitem.price
            existing_cart_item.price = existing_cart_item.unit_price * existing_cart_item.quantity
            existing_cart_item.save()
            return existing_cart_item
        else:
            # If not, create new entry
            unit_price = menuitem.price
            total_price = unit_price * quantity

            validated_data['user'] = user
            validated_data['unit_price'] = unit_price
            validated_data['price'] = total_price

            return super().create(validated_data)
