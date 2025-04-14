from django.urls import path
from . import views
from .views import AssignDeliveryView, ManagerGroupView,CartView, OrderDetailView

urlpatterns = [
    path('menu-items/', views.MenuItemListView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('create-category/', views.CreateCategory.as_view()),
    path('categories/', views.CategoryListView.as_view()),
    path("groups/manager/users", ManagerGroupView.as_view()),
    path("groups/manager/users/<int:user_id>", ManagerGroupView.as_view()),
    path('groups/delivery-crew/users/', AssignDeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:user_id>', AssignDeliveryView.as_view()),
    path('cart/menu-items/', CartView.as_view()),
    path('cart/menu-items/', views.CartView.as_view(), name='cart-menu-items'),
    path('cart/menu-items/<int:item_id>/', CartView.as_view(), name='cart-item-delete'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),

]
