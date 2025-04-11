from django.urls import path
from . import views
from .views import AssignGroupView, RemoveGroupView

urlpatterns = [
    path('menu-items/create/', views.CreateMenuItemView.as_view()),
    path('menu-items/', views.MenuItemList.as_view()),
    path('create-category/', views.CreateCategory.as_view()),
    path('categories/', views.CategoryListView.as_view()),
    path('users/group/', AssignGroupView.as_view(), name='assign-group'),
    path('users/group/remove/', RemoveGroupView.as_view(), name='remove-group'),

]
