from django.urls import path
from . import views
from .views import AssignDeliveryView, AssignGroupView, RemoveDeliveryView, RemoveGroupView

urlpatterns = [
    path('create/', views.CreateMenuItemView.as_view()),
    path('menu-items/', views.MenuItemListView.as_view()),
    path('create-category/', views.CreateCategory.as_view()),
    path('categories/', views.CategoryListView.as_view()),
    path('users/group/', AssignGroupView.as_view(), name='assign-group'),
    path('users/group/remove/', RemoveGroupView.as_view(), name='remove-group'),
    path('users/group/delivery/', AssignDeliveryView.as_view(), name='assign-delivery'),
    path('users/group/delivery/remove/', RemoveDeliveryView.as_view(), name='remove-delivery'),

]
