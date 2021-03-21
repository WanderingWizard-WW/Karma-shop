from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from Shop.mixins import CartMixin, ProductFilter
from Shop.models import *
from .forms import OrderForm, RegistrationForm, LoginForm
from .utils import recalc_cart


### Домашняя страница
class HomeView(View):
    def get(self, request, *args, **kwargs):
        latest_products = Product.objects.all().order_by('-id')[:8]
        latest_sandals = Product.objects.all().order_by('-id')[:8]
        categorys = Category.objects.all()
        return render(request, 'index.html', {'products': latest_products, 'categorys': categorys})


#### Просмотр продуктов ####
### Страница продукта
class ProductDetailView(CartMixin, DetailView):
    queryset = Product.objects.all()
    template_name = 'single-product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorys"] = self.categories
        return context


### Страница товаров с фильтром
class AdvancedFilter(ProductFilter, ListView):
    template_name = "category.html"
    paginate_by = 6

    def get_queryset(self):
        products = Product.objects.all()
        a = self.request.GET.getlist('category')
        b = self.request.GET.getlist('brand')
        c = self.request.GET.getlist('material')
        all_set = False
        if a and b:
            if c:
                all_set = True
        if a:
            products = products.filter(category__slug__in=a)
            if all_set:
                products = products.filter(Q(brand__title__in=b) and Q(material__title__in=c))
            elif b:
                products = products.filter(Q(brand__title__in=b) or Q(material__title__in=c))
        elif b or c:
            products = products.filter(Q(brand__title__in=b) | Q(material__title__in=c))
        return products

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['category'] = ''.join([f"category={x}&" for x in self.request.GET.getlist("category")])
        context['brand'] = ''.join([f"brand={x}&" for x in self.request.GET.getlist("brand")])
        context['material'] = ''.join([f"material={x}&" for x in self.request.GET.getlist("material")])
        context["categorys"] = self.get_category()
        return context


#### Просмотр продуктов ####
#### Работа с корзиной ####
### Страница корзины
class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'cart': self.cart,
            'categorys': self.categories
        }
        return render(request, 'cart.html', context)


### Добавить товар в корзину
class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, product=product
        )
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')


### Удалить товар из корзины
class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')


### Изменить колличевство товара
class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')


### Страница оформления заказа
class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categorys': self.categories,
            'form': form
        }
        return render(request, 'checkout.html', context)


#### Работа с корзиной ####


#### Вьюшки регестрации и авторизации ####
### Cтраница авторизации
class LoginView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form, 'categories': self.categories, 'cart': self.cart}
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form, 'categories': self.categories, 'cart': self.cart}
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'login.html', context)


### Страница регестрации
class RegistrationView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {'form': form, 'categories': self.categories, 'cart': self.cart}
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {'form': form, 'categories': self.categories, 'cart': self.cart}
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        return render(request, 'registration.html', context)


#### Вьюшки регестрации и авторизации и профиля

### Профиль покупателя
class ProfileView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
        context = {'orders': orders, 'categories': self.categories, 'cart': self.cart}
        return render(request, 'profile.html', context)


#### Вьюшки регестрации и авторизации и профиля ####

### Страница после оформления заказа
class AfterOrderView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.filter(customer=customer).order_by('-created_at').first()
        context = {'order': order, 'categories': self.categories, 'cart': self.cart}
        return render(request, 'confirmation.html', context)


### Страница деталей заказаэ
class OrderCheckView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.filter(customer=customer)
        order = order.get(id=kwargs.get('slug'))
        context = {'order': order, 'categories': self.categories, 'cart': self.cart}
        return render(request, 'order_info.html', context)


### Сделать заказ
class MakeOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            return HttpResponseRedirect('/after-order/')
        return HttpResponseRedirect('/checkout/')
