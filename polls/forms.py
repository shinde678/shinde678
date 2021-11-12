from django import forms
from polls.models import * 
from decimal import Decimal
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext, gettext_lazy as _

# Login form view
class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus':True, 'class':'form-control'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
    )

# Menu form class
class MenuForm(forms.ModelForm):
    menu_name = forms.CharField(widget=forms.TextInput
        (attrs={'class':'form-control','placeholder':'Enter Menu Name'}))	        

    status = forms.IntegerField(widget=forms.HiddenInput(),initial=1)   

    class Meta:
        model = Menu
        fields = ['menu_name', 'status']

    def clean_menu_name(self):
        menuname = self.cleaned_data['menu_name']

        if menuname is not None:
            if not all(i.isalpha() or i.isspace() for i in menuname):
                raise forms.ValidationError("Accept only characters.")
        else:
            raise forms.ValidationError("Required this field.")
        return self.cleaned_data['menu_name']	   


# Add New Raw Material Form
class AddRawMaterialForm(forms.ModelForm):
    raw_item = forms.CharField(widget=forms.TextInput
        (attrs={'class':'form-control', 'placeholder':'Enter Item Name'}))

    status = forms.IntegerField(widget=forms.HiddenInput(),initial=1)

    class Meta:
        model = RawMaterialItem
        fields = ['raw_item', 'status']

    def clean_raw_item(self):
        raw_item = self.cleaned_data['raw_item']
        
        if raw_item is not None:
            if not all(i.isalpha() or i.isspace() for i in raw_item):
                raise forms.ValidationError("Accept only characters.")
        else:
            raise forms.ValidationError("Required this field.") 
        return self.cleaned_data['raw_item']           

#Add Stock Form    
class RawMaterialStockForm(forms.ModelForm):
   
    stock_kg_qty = forms.FloatField(widget=forms.TextInput
        (attrs={'class':'form-control', 'placeholder':'Enter Kg / Qty'}))

    price = forms.FloatField(widget=forms.TextInput
        (attrs={'class':'form-control', 'placeholder':'Enter Price'}))    

    status = forms.IntegerField(widget=forms.HiddenInput(),initial=1)    

    class Meta:
        model = AddStockTmp
        fields = ['stock_item', 'stock_kg_qty', 'price', 'status']    

    # form view
    def __init__(self, *args, **kwargs):
        super(RawMaterialStockForm, self).__init__(*args, **kwargs)
        self.fields['stock_item'].label = "Select Item"
        self.fields['stock_kg_qty'].label = "Enter Kg / Qty"	
        self.fields['price'].label = "Enter Price" 

    def clean_stock_kg_qty(self):
        stock_kg_qty = self.cleaned_data['stock_kg_qty']

        if Decimal(stock_kg_qty) is not None:
            if not Decimal(stock_kg_qty):
                raise forms.ValidationError("Accept only digit 0-9")
        else:
            raise forms.ValidationError("Required this field.")        
        return self.cleaned_data['stock_kg_qty']

    def clean_price(self):
        price = self.cleaned_data['price']

        if Decimal(price) is not None:
            if not Decimal(price):
                raise forms.ValidationError("Accept only digit 0-9")
        else:
            raise forms.ValidationError("Required this field.")        
        return self.cleaned_data['price']    


# Stock Update Form
class StockUseForm(forms.ModelForm):
    kg_qty = forms.FloatField(widget=forms.TextInput
		(attrs={'class':'form-control','placeholder':'Enter Kg / Qty', 'required': 'true'}))
  
    stock_kg_qty = forms.CharField(widget=forms.TextInput
		(attrs={'class':'form-control text-danger font-weight-bold', 'readonly':'readonly'}))   

    class Meta:
        model = AddStockTmp
        fields = ['stock_kg_qty', 'status']

    def __init__(self, *args, **kwargs):
        super(StockUseForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget = forms.HiddenInput()
        self.fields['kg_qty'].label = "Enter Kg / Qty"

    def clean_kg_qty(self):
        kg_qty = self.cleaned_data['kg_qty']

        if Decimal(kg_qty) is not None:
            if not Decimal(kg_qty):
                raise forms.ValidationError("Accept only digit 0-9")
        else:
            raise forms.ValidationError("Required this field.")        
        return self.cleaned_data['kg_qty']    


# Report Form
class StockReportForm(forms.ModelForm):
    from_date = forms.DateField(widget=forms.TextInput
            (attrs={'type':'date','class':'form-control'}))

    to_date = forms.DateField(widget=forms.TextInput
            (attrs={'type':'date','class':'form-control'}))	

    status = forms.IntegerField(widget=forms.HiddenInput(),initial=1)

    class Meta:
        model = StockReport
        fields = ['from_date', 'to_date', 'stock_item', 'list_name']	

    def __init__(self, *args, **kwargs):
        super(StockReportForm, self).__init__(*args, **kwargs)
        self.fields['list_name'].label = "Select Report Format"	
        self.fields['stock_item'].label = "Select Item"	
        self.fields['from_date'].required = False
        self.fields['to_date'].required = False
        self.fields['stock_item'].required = False
        self.fields['stock_item'].widget.attrs.update({'class': 'selectbox class-form-control'})        

# End Report form content

# Expenses Form content

# Expeses form class
class ExpesesForm(forms.ModelForm):
    expenses_name = forms.CharField(widget=forms.TextInput
        (attrs={'class':'form-control','placeholder':'Enter Expeses'}))	        

    status = forms.IntegerField(widget=forms.HiddenInput(),initial=1)   

    class Meta:
        model = ExpesesList
        fields = ['expenses_name', 'status']

    def clean_expenses_name(self):
        expeses = self.cleaned_data['expenses_name']

        if expeses is not None:
            if not all(i.isalpha() or i.isspace() for i in expeses):
                raise forms.ValidationError("Accept only characters.")
        else:
            raise forms.ValidationError("Required this field.")
        return self.cleaned_data['expenses_name']

# paid Expeses form
class PaidExpesesForm(forms.ModelForm):
    expenses_amount = forms.CharField(widget=forms.TextInput
        (attrs={'class':'form-control','placeholder':'Enter Amount'}))

    desc = forms.CharField(widget=forms.Textarea
        (attrs={'rows':'3','class':'form-control', 'placeholder':'Eneter Description'}))    	        

    status = forms.IntegerField(widget=forms.HiddenInput(),initial=1)   

    class Meta:
        model = ExpensesMaster
        fields = ['expenses', 'expenses_amount', 'desc', 'status']

    def __init__(self, *args, **kwargs):
        super(PaidExpesesForm, self).__init__(*args, **kwargs)
        self.fields['desc'].label = "Enter Description"	
        self.fields['expenses_amount'].label = "Amount"
            

    def clean_kg_qty(self):
        exp_amount = self.cleaned_data['expenses_amount']

        if Decimal(exp_amount) is not None:
            if not Decimal(exp_amount):
                raise forms.ValidationError("Accept only digit 0-9")
        else:
            raise forms.ValidationError("Required this field.")        
        return self.cleaned_data['expenses_amount']          


# Date Wise Report Form
class DateWiseReport(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput
            (attrs={'type':'date','class':'form-control'}))

    to_date = forms.DateField(widget=forms.TextInput
            (attrs={'type':'date','class':'form-control'}))	

    def __init__(self, *args, **kwargs):
        super(DateWiseReport, self).__init__(*args, **kwargs)
        self.fields['from_date'].required = False
        self.fields['to_date'].required = False
               