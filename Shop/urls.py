from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('filter/', AdvancedFilter.as_view(), name='filter'),
    path('products/<str:slug>', ProductDetailView.as_view(), name='detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('change-qty/<str:slug>/', ChangeQTYView.as_view(), name='change_qty'),
    path('remove-from-cart/<str:slug>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('add-to-cart/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('after-order/', AfterOrderView.as_view(), name='check_order'),
    path('order-info/<str:slug>', OrderCheckView.as_view(), name='order_info'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
