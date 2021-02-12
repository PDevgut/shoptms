from django.urls import path, include

from src.app.index import views
from src.app.cart.views import AddToCartView


urlpatterns = [
    path ('', views.IndexView.as_view(), name='index'),
    path ('cart/', include("src.app.cart.urls")),
    path ('notebook/<str:slug>/', views.NotebookDetailView.as_view() , name = 'notebook_detail'),
    path ('smartphone/<str:slug>/', views.SmartphoneDetailView.as_view() , name = 'smartphone_detail'),
    path ('category/<str:slug>/', views.CategoryDetailView.as_view(), name = 'category_detail'),
    path ('<str:ct_model>/<str:slug>/add/<str:pk>', AddToCartView.as_view(), name = 'add_to_card')
]
