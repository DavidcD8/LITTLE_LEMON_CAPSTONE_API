from django.urls import path
from . import views
from .views import AssignDeliveryView, ManagerGroupView

urlpatterns = [
    path('menu-items/', views.MenuItemListView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('create-category/', views.CreateCategory.as_view()),
    path('categories/', views.CategoryListView.as_view()),
    path("groups/manager/users", ManagerGroupView.as_view(), name="add-manager"),
    path("groups/manager/users/<int:user_id>", ManagerGroupView.as_view(), name="remove-manager"),
    path('groups/delivery-crew/users/', AssignDeliveryView.as_view(), name='assign-delivery'),
    path('groups/delivery-crew/users/<int:user_id>', AssignDeliveryView.as_view(), name='assign-delivery'),

]
