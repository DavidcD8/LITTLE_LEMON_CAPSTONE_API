from django.urls import path
from . import views
 
urlpatterns = [
    path('menu-items/create/', views.CreateMenuItemView.as_view()),
    path('menu-items/', views.MenuItemList.as_view()),
   

]
