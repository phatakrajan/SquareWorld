from .views import ProductListView
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from SquareWorld import settings
from SquareVeg.views import CartView
from SquareVeg import views
from SquareVeg.registerloginview import RegisterView, LoginView

urlpatterns = [
    url(r'^$', ProductListView.as_view(), name='SquareVeg'),        
    url(r'^(?P<pk>\d+)$', ProductListView.as_view(), name='SquareVeg_Category'),        
    url(r'^register$', RegisterView.as_view(), name='register'),        
    url(r'^login/$', LoginView.as_view(), name='login'),        
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^admin/', include(admin.site.urls)),
    ] 