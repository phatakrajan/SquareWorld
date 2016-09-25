
from django.views.generic.base import TemplateView
from django.shortcuts import render
from SquareVeg.models import Addresses
from django.http.response import HttpResponseRedirect

class AddressView(TemplateView):
    """description of class"""
    template_name = "SquareVeg/address.html"

    def get(self, request, *args, **kwargs):
        # super(RegisterView, self).get(request, *args, **kwargs)\                    
        addresses = Addresses.objects.filter(user_id=request.user.id)
        errors = []
        return render(request,'SquareVeg/address.html',{'errors': errors, 'addresses' : addresses}) 

    def post(self, request, *args, **kwargs):
        errors = []
        # check whether it's valid:
        if not request.POST.get('name', ''):
            errors.append('Enter a name.')
        if not request.POST.get('address', ''):
            errors.append('Enter an address.')
        if not errors:
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            Addresses.objects.create(user_id=request.user,
                             user_name = request.POST['name'],
                             city=request.POST['city'],
                             street_address = request.POST['address'],
                             landmark = request.POST['landmark'],
                             pincode = request.POST['pincode']
                             )
            return HttpResponseRedirect('./address')

        return render(request,'SquareVeg/address.html',{'errors': errors, 'addresses' : addresses})
