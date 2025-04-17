from django.urls import path
from . import views
from .views import AssignDeliveryView, ManagerGroupView,CartView, OrderDetailView, OrderListView

urlpatterns = [
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleItemView.as_view()),
    path('create-category/', views.CreateCategory.as_view()),
    path('categories/', views.CategoryListView.as_view()),
    path("groups/manager/users", ManagerGroupView.as_view()),
    path("groups/manager/users/<int:user_id>", ManagerGroupView.as_view()),
    path('groups/delivery-crew/users/', AssignDeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:user_id>', AssignDeliveryView.as_view()),
    path('cart/menu-items/', CartView.as_view()),
    path('cart/menu-items/', views.CartView.as_view(), name='cart-menu-items'),
    path('cart/menu-items/<int:item_id>/', CartView.as_view(), name='cart-item-delete'),
    path('orders/', OrderListView.as_view(), name='order-list'),  # for listing and posting orders
    path('orders/<int:pk>/', OrderListView.as_view(), name='order-detail'),  # for updating a single order
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),

]
