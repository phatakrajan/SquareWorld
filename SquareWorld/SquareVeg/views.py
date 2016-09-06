# Create your views here.
from django.core.exceptions import ImproperlyConfigured
from django_filters.filters import CharFilter, NumberFilter
from SquareVeg.models import Product, Category, Cart, CartItem
from django_filters.filterset import FilterSet
from django.views.generic.list import ListView
from django.db.models.query_utils import Q
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.http.response import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin

class FilterMixin(object):
	filter_class = None
	search_ordering_param = "ordering"

	def get_queryset(self, *args, **kwargs):
		try:
			qs = super(FilterMixin, self).get_queryset(*args, **kwargs)
			return qs
		except:
			raise ImproperlyConfigured("You must have a queryset in order to use the FilterMixin")

	def get_context_data(self, *args, **kwargs):
		context = super(FilterMixin, self).get_context_data(*args, **kwargs)
		qs = self.get_queryset()
		ordering = self.request.GET.get(self.search_ordering_param)
		if ordering:
			qs = qs.order_by(ordering)
		filter_class = self.filter_class
		if filter_class:
			f = filter_class(self.request.GET, queryset=qs)
			context["object_list"] = f
		return context

class ProductFilter(FilterSet):
	title = CharFilter(name='title', lookup_type='icontains', distinct=True)
	category = CharFilter(name='categories__title', lookup_type='icontains', distinct=True)
	category_id = CharFilter(name='categories__id', lookup_type='icontains', distinct=True)
	min_price = NumberFilter(name='Product__price', lookup_type='gte', distinct=True) # (some_price__gte=somequery)
	max_price = NumberFilter(name='Product__price', lookup_type='lte', distinct=True)
	class Meta:
		model = Product
		fields = [
			'min_price',
			'max_price',
			'category',
			'title',
			'description',
		]

class ProductListView (FilterMixin, ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = "SquareVeg/products.html"
    filter_class = ProductFilter

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get("q") #None
        context["categories"] = Category.objects.all()
        #context["cart"] = Cart.objects.get(user__id = self.request.user.id)
        return context

    def get_queryset(self, *args, **kwargs):
        #qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        if 'pk' in self.kwargs:
            qs = Product.objects.filter(categories__pk=self.kwargs['pk'])
        else:
            qs = Product.objects.all()
        query = self.request.GET.get("q")
        if query:
            qs = self.model.objects.filter(
	            Q(title__icontains=query) |
	            Q(description__icontains=query)
	            )
            try:
                qs2 = self.model.objects.filter(
	                Q(price=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs

class CartView(LoginRequiredMixin,SingleObjectMixin, View):
    
    model = Cart
    template_name = "SquareVeg/checkout.html"

    def get_object(self, *args, **kwargs):
        #self.request.session.set_expiry(5) #5 mincart_idutes
        try:        
            cart = Cart.objects.get(user__id = self.request.user.id)
            #cart_id = cart.id

        except Cart.DoesNotExist:
            cart = Cart()
            cart.tax_percentage = 0.075
            cart.save()
            #cart_id = cart.id


        #if cart_id == None:
        #    cart = Cart()F
        #    cart.tax_percentage = 0.075
        #    cart.save()
        #    cart_id = cart.id
        #    self.request.session["cart_id"] = cart_id
            
        #cart = Cart.objects.get(id=cart_id)

        if self.request.user.is_authenticated():
            cart.user = self.request.user
            cart.save()

        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        item_id = request.GET.get("item")
        delete_item = request.GET.get("delete", False)
        flash_message = ""
        item_added = False
        if item_id:
            item_instance = get_object_or_404(Product, id=item_id)
            qty = request.GET.get("qty", 1)
            try:
                if Decimal(qty,2) < 1:
                    delete_item = True
            except:
                raise Http404
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            if created:
                flash_message = "Successfully added to the cart"
                item_added = True
                cart_item.quantity = Decimal(qty)
            if delete_item:
                flash_message = "Item removed successfully."
                cart_item.delete()
            else:
                if not created:
                    flash_message = "Quantity has been updated successfully."
                    cart_item.quantity = cart_item.quantity + Decimal(qty)
                cart_item.save()
            if not request.is_ajax():
                return HttpResponseRedirect(reverse("cart"))
				#return cart_item.cart.get_absolute_url()
        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None
            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None

            try:
                cart_total = cart_item.cart.total
            except:
                cart_total = None

            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None

            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0

            data = {
		            "deleted": delete_item, 
		            "item_added": item_added,
		            "line_total": total,
		            "subtotal": subtotal,
		            "cart_total": cart_total,
		            "tax_total": tax_total,
		            "flash_message": flash_message,
		            "total_items": total_items
		            }

            return JsonResponse(data) 


        context = {
        "object": self.get_object()
        }
        template = self.template_name
        return render(request, template, context)

def register(request):
    return render(request,'SquareVeg/register.html')