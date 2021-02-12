from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from src.app.cart import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path("<str:pk>/delete/", csrf_exempt(views.DeleteView.as_view())),
    path("<str:pk>/update/", csrf_exempt(views.UpdateView.as_view())),
    path('order/', views.OrderView.as_view(), name='order'),
    path('make_order/', views.MakeOrderView.as_view(), name='make_order')


]
