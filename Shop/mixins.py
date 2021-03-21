from django.views.generic import View

from .models import Cart, Customer, ProductMaterial, ProduсtContry, ProduсtBrand, Category, Product


class CartMixin(View):
    categories = Category.objects.all()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)


class ProductFilter:
    def get_material(self):
        return ProductMaterial.objects.all()

    def get_contry(self):
        return ProduсtContry.objects.all()

    def get_brand(self):
        return ProduсtBrand.objects.all()

    def get_category(self):
        return Category.objects.all()

    def get_all_products(self):
        return Product.objects.filter(available=True)
