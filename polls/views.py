from django.db.models.base import Model
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User 
from django.contrib import messages
from polls.forms import *
from .models import *
from django.views.generic import ListView
from django.http import Http404
import reportlab
from io import BytesIO
from django.http import FileResponse
from reportlab.pdfgen import canvas
import csv
from datetime import date
from django.db.models import Q
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.views import View
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from decimal import Decimal
from django.db.models import F
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import redirect
from .forms import LoginForm
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.urls import reverse
from datetime import date
from django.db.models import Sum, Max
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count


''' Authenticate content '''

class LoggedInMixin(object):
    """ A mixin requiring a user to be logged in. """
    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('/polls/login/')
        return super(LoggedInMixin, self).dispatch(request, *args, **kwargs)

# Show Login page 
class MyLoginView(LoginView):
    template_name='login.html'
    authentication_form=LoginForm

# Logout page content
class MyLogoutView(LogoutView):
    template_name='logout.html'

# Show Dashboard
class MyDashboardView(LoggedInMixin,ListView):
    model = AddStockTmp
    template_name='dashboard.html' 
    
    def get_context_data(self, **kwargs):
        #Remaning Stock
        context = super(MyDashboardView, self).get_context_data(**kwargs)
        context['stock_list'] = AddStockTmp.objects.filter(status=1).order_by('stock_kg_qty')

        # Today Orders    
        today = date.today()
        total_orders = Orders.objects.filter(item_date = today).count()        
        context['order_list'] = total_orders

        # Today Earn
        total_earn = Orders.objects.filter(item_date=today, status=1).aggregate(Sum('item_total'))
        context['earn_list'] = total_earn
        
        # Resatraunt Menu
        total_menu = Menu.objects.filter(status=1).count()
        context['menu_list'] = total_menu

        # Stock Item
        stock_item = RawMaterialItem.objects.filter(status=1).count()
        context['raw_item_list'] = stock_item

        #Today sale summary
        item = []
        qtyDataData = []
        obj1 = Menu.objects.values('id', 'menu_name').filter(status=1).order_by('-id')
        for i in obj1:
            item.append(i['menu_name'])

            q = Orders.objects.filter(item_date=(today), item_name=i['id'])
            saleData = q.aggregate(Sum('item_qty'))
            
            if not q:
                qtyDataData.append(0)
            else:                           
                qtyDataData.append(saleData)              

        data = zip(item, qtyDataData)
        context['order_data'] = data 
        return context


# Chanage Password View
class MyPasswordChangeView(LoggedInMixin,PasswordChangeView):
    template_name='changepass.html'
    success_url='/To_Keep_Account/changepassdone/'	

# Password Chnage Successfully View
class MyPasswordChangeDoneView(LoggedInMixin,PasswordChangeDoneView):
    template_name='changepassdone.html'

''' End authenticate content '''

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


""" Menu Content """

# Show Menu View
class ShowMenuListView(LoggedInMixin,ListView):	
    model = Menu
    template_name = 'manage_menu.html'  
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    queryset = Menu.objects.filter(status=1) 

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ShowMenuListView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ShowMenuListView, self).get_context_data(*args, **kwargs)  

# Create new Menu content
class CreateMenuView(LoggedInMixin, SuccessMessageMixin, CreateView):
	model = Menu
	template_name = 'add_menu.html'
	form_class = MenuForm 
	success_url = reverse_lazy('manageMenu')
	success_message = "%(menu_name)s Was Created Successfully"
	
	def form_valid(self,form):
		return super().form_valid(form)

	def form_invalid(self, form):
		return self.render_to_response(self.get_context_data(form=form)) 

# Update Menu View
class MenuUpdateView(LoggedInMixin, SuccessMessageMixin, UpdateView):
    model = Menu
    template_name  = 'edit_menu.html'
    form_class = MenuForm	
    success_url = reverse_lazy('manageMenu')
    success_message = "%(menu_name)s Was Update Successfully"

    def form_valid(self,form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# Delete Menu
class DeleteMenuView(LoggedInMixin,RedirectView):
	url = '/polls/manageMenu'

	def get_redirect_url(self, *args, **kwargs):
		del_id = kwargs['slug']
		Menu.objects.filter(slug=del_id).update(status=2)
		return super().get_redirect_url(*args, **kwargs)      

""" End Menu Content """            

""" Manage order content """

# Manage order view content
class ManageOrderView(LoggedInMixin ,ListView):
    model = Menu
    template_name = 'manage_order.html'
    
    def get_context_data(self, **kwargs):
        context = super(ManageOrderView, self).get_context_data(**kwargs)
        context['last_invoice'] = Invoice.objects.all().order_by('-id')[:1]
        context['menus'] = Menu.objects.filter(status=1)
        return context

# Create new order view content
class CreateOrderView(LoggedInMixin, CreateView):    
    def post(self, request):
        if request.method=='POST':
            menu_id = request.POST.getlist("menu_name[]")
            price = request.POST.getlist("item_price[]")
            qty = request.POST.getlist("item_quantity[]")
            total = request.POST.getlist("item_total[]")
            finaltotal = request.POST["finaltotal"]
            billno = request.POST["billno"]
            quantity = request.POST["quantity"]
            today = date.today()

            if OrdersMaster.objects.filter(master_date=today).exists():
                invoice_obj = Invoice(invoice_no=billno, invoice_item_quantity=quantity, invoice_item_final_total=finaltotal, invoice_date=today)
                invoice_obj.save()

                for i in range(0,len(menu_id)):
                    menu_name = menu_id[i]
                    menu_price = price[i]
                    menu_qty = qty[i]
                    menu_total = total[i]
                    menu_name_obj = Menu.objects.get(id=menu_name)
                    order_obj = Orders(invoice_no=billno, item_name=menu_name_obj, item_price=menu_price, item_qty=menu_qty, item_total=menu_total, item_date=today)
                    order_obj.save()

                messages.success(self.request, 'Successfully Add Order')			
                return redirect('/polls/showOrder')
            else:
                master_obj = OrdersMaster(master_date=today)
                master_obj.save()

                invoiceobj = Invoice(invoice_no=billno, invoice_item_quantity=quantity, invoice_item_final_total=finaltotal, invoice_date=today)
                invoiceobj.save()

                for i in range(0,len(menu_id)):
                    menu_name = menu_id[i]
                    menu_price = price[i]
                    menu_qty = qty[i]
                    menu_total = total[i]
                    menu_name_obj = Menu.objects.get(id=menu_name) 
                    orderobj = Orders(invoice_no=billno, item_name=menu_name_obj, item_price=menu_price, item_qty=menu_qty, item_total=menu_total, item_date=today)
                    orderobj.save()
            messages.success(self.request, 'Successfully Add Order')			
            return redirect('/polls/showOrder')     


# Show order (Display last order create content)
class ShowOrderListView(LoggedInMixin, ListView):
    model = Orders
    template_name = 'show_order.html'
    
    def get_context_data(self, **kwargs):
        context = super(ShowOrderListView, self).get_context_data(**kwargs)
        obj = Invoice.objects.all().order_by('-id')[:1]
        context['last_invoice'] = Invoice.objects.all().order_by('-id')[:1]
        for i in obj:
            context['last_order'] = Orders.objects.filter(invoice_no=i.invoice_no)
        return context

# Show order view date wise detials content
class ShowOrderPrintView(LoggedInMixin, ListView):
    model = Orders
    template_name = 'prints/print_bill.html'

    def get_context_data(self, **kwargs):
        context = super(ShowOrderPrintView, self).get_context_data(**kwargs)
        obj = Invoice.objects.all().order_by('-id')[:1]
        context['last_invoice'] = Invoice.objects.all().order_by('-id')[:1]
        for i in obj:
            context['last_order'] = Orders.objects.filter(invoice_no=i.invoice_no)
        return context
""" End manage content order """           

""" Bills Content """

# Show bill content invoice number wise
class ShowBillsListView(LoggedInMixin, ListView):
    model = Invoice
    template_name = 'show_bill.html'    
    paginate_by = 10
    paginate_orphans = 1

    ordering = ['-created_at']

    queryset = Invoice.objects.filter(status=1)

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ShowBillsListView,self).get_context_data(*args, **kwargs)
        except:
            self.kwargs['page'] = 1
            return super(ShowBillsListView, self).get_context_data(*args, **kwargs)

# view order bill number content
class ViewOrderListView(LoggedInMixin, ListView):
    model = Orders
    template_name = 'view_order.html'
    paginate_by = 10
    paginate_orphans = 1
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super(ViewOrderListView, self).get_context_data(**kwargs)
        context['order_list'] = Orders.objects.filter(invoice_no=self.kwargs['invoice_no'])
        context['invoice_list'] = Invoice.objects.filter(invoice_no=self.kwargs['invoice_no'])
        return context

# Receipt bill print content 
class ViewRecieptBillView(LoggedInMixin, ListView):
    model = Orders
    template_name = 'prints/reciept_print.html'

    def get_context_data(self, **kwargs):
        context = super(ViewRecieptBillView, self).get_context_data(**kwargs)
        obj = Invoice.objects.filter(invoice_no=self.kwargs['invoice_no'])
        context['last_invoice'] = Invoice.objects.filter(invoice_no=self.kwargs['invoice_no'])
        context['last_order'] = Orders.objects.filter(invoice_no=self.kwargs['invoice_no'])
        return context


class ViewOrderDetialsView(LoggedInMixin, ListView):
    model = OrdersMaster
    template_name = 'date_wise_orders.html'
    ordering = ['-created_at']

    queryset = OrdersMaster.objects.all()

class ViewDateWiseOrderDetialsView(LoggedInMixin, ListView):
    model = Orders
    template_name = 'date_wise_order_detials.html'
    paginate_by = 10
    paginate_orphans = 1

    def get_context_data(self, **kwargs):
        context = super(ViewDateWiseOrderDetialsView, self).get_context_data(**kwargs)
        obj = OrdersMaster.objects.get(id=self.kwargs['pk'])
        itemdate = obj.master_date
        context['date_obj'] = OrdersMaster.objects.filter(id=self.kwargs['pk'])
        # Retrive record date wise from orders
        context['order_list'] = Orders.objects.filter(item_date=itemdate)
        # split record date wise
        context['split_order'] = Invoice.objects.filter(invoice_date=itemdate,status=1)
        return context
        

# View order PDF report content       
class ViewOrderPDFReportView(LoggedInMixin, ListView):
    model = Orders
    template_name = 'reports/order_report.html'

    def get_context_data(self, **kwargs): 
        try:      
            context = super(ViewOrderPDFReportView, self).get_context_data(**kwargs)
            obj = OrdersMaster.objects.get(id=self.kwargs['pk'])
            itemdate = obj.master_date
            context['date_obj'] = OrdersMaster.objects.filter(id=self.kwargs['pk'])
            # Retrive record date wise from orders
            context['order_list'] = Orders.objects.filter(item_date=itemdate)
            # split record date wise
            context['split_order'] = Invoice.objects.filter(invoice_date=itemdate,status=1)
            return context
        except Http404:
            self.kwargs['page'] = 1
            return super(VillageListView, self).get_context_data(*args, **kwargs)    

    def render_to_response(self, context, **kwargs):
        pdf = render_to_pdf(self.template_name, context)
        return HttpResponse(pdf, content_type='application/pdf')


# View order CSV report
class ViewOrderCSVReportView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        response['Content-Disposition'] = 'attachment; filename="Order_'+ d1 +'.csv"'

        writer = csv.writer(response)

        obj = OrdersMaster.objects.get(id=self.kwargs['pk'])
        itemdate = obj.master_date
        date_obj = OrdersMaster.objects.filter(id=self.kwargs['pk'])
        # Retrive record date wise from orders
        order_list = Orders.objects.filter(item_date=itemdate)
        # split record date wise
        split_order = Invoice.objects.filter(invoice_date=itemdate,status=1)

        for i in date_obj:
            row = ['', 'Date :', i.master_date]
            writer.writerow(row)

        writer.writerow(['Item Name', 'Price', 'Quantity', 'Total'])

        for j in split_order:
            blank_row = ['']
            row = ['', 'Bill No :', j.invoice_no]
            blank_row = ['']
            writer.writerow(row)
            writer.writerow(blank_row)
            for i in order_list:
                if i.invoice_no == j.invoice_no:
                    orders_list = [i.item_name, i.item_price, i.item_qty, i.item_total]
                    writer.writerow(orders_list) 
            row1 = ['Total', '', j.invoice_item_quantity, j.invoice_item_final_total]
            writer.writerow(row1) 

        return response          
         
""" End Bill Contents """

""" Data Visualisation content """

class ChartData(APIView):
    def get(self, request, format=None):
        labels = []
        defaultData = []

        obj1 = Menu.objects.values('id', 'menu_name').filter(status=1)
        for i in obj1:
            labels.append(i['menu_name'])

            q = Orders.objects.values('item_name').annotate(items=Sum('item_qty')).filter(item_name=i['id'])
            for entry in q:
                defaultData.append(entry['items'])
               

        data = {
        "labels": labels,
        "defaultData": defaultData,
        }
        return JsonResponse(data={
           'labels': labels,
           'defaultData': defaultData,
        })

# Bar Chart Visualization
class ViewBarVisualizationView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'barchart.html')        

# Line Chart Visualization
class ViewLineVisualizationView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'line_chart.html')

# Pie Chart Visualization
class ViewPieVisualizationView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pie_chart.html') 
        
# Filter Chart Data View
class ChartDataFilter(APIView):
    def get(self, request, format=None):
        if request.method == 'GET':            
            labels = []
            defaultData = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']
           
            if fromdate is not None and todate is not None:
                obj1 = Menu.objects.values('id', 'menu_name').filter(status=1).order_by('-id')
                for i in obj1:
                    labels.append(i['menu_name'])

                    q = Orders.objects.values('item_name').annotate(items=Sum('item_qty')).filter(item_date__range=(fromdate,todate),item_name=i['id']).order_by('item_qty')
                    if not q:
                        defaultData.append(0)
                    else:                           
                        for entry in q:
                            defaultData.append(entry['items'])

        data = {
        "labels": labels,
        "defaultData": defaultData,
        }
        return JsonResponse(data={
           'labels': labels,
           'defaultData': defaultData,
        })   

# Bar Chart Visulisation
class ViewBarChartsFilterView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'bar_chart_filter.html') 

# Line Chart Visulisation
class ViewLineChartsFilterView(LoggedInMixin, View):
    def get(self, request, * args, **kwargs):
        return render(request, 'line_chart_filter.html')

# Pie Chart Visulisation
class ViewPieChartFilterView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pie_chart_filter.html')             

""" End data visulisation content """    


""" Raw Material content """

# Show raw material list
class ViewManageRawMaterialView(LoggedInMixin, ListView):
    model = RawMaterialItem
    template_name = 'manage_raw_material.html'  
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    queryset = RawMaterialItem.objects.filter(status=1) 

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewManageRawMaterialView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewManageRawMaterialView, self).get_context_data(*args, **kwargs) 

# Raw material create view
class ViewCreateRawMaterialView(LoggedInMixin, SuccessMessageMixin, CreateView):
    model = RawMaterialItem
    template_name = 'add_raw_material.html'
    form_class = AddRawMaterialForm
    success_url = reverse_lazy('manageRawMaterial')
    success_message = "%(raw_item)s Was Created Successfully"

    def form_valid(self,form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# Raw material update view
class ViewRawMaterialUpdateView(LoggedInMixin, SuccessMessageMixin, UpdateView):
    model = RawMaterialItem
    template_name = 'edit_raw_material.html'
    form_class = AddRawMaterialForm
    success_url = reverse_lazy('manageRawMaterial')
    success_message = "%(raw_item)s Was Update Successfully"

    def form_valid(self,form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# Delete raw material item   
class ViewRawMaterialDeleteView(LoggedInMixin, RedirectView):
	url = '/polls/manageRawMaterial'

	def get_redirect_url(self, *args, **kwargs):
		del_id = kwargs['pk']
		RawMaterialItem.objects.filter(id=del_id).update(status=2)
		return super().get_redirect_url(*args, **kwargs)           
	
""" End raw material content """

""" Raw material content """
# Raw material stock view
class ViewRawmaterialStockView(LoggedInMixin, ListView):
    model = AddStockTmp
    template_name = 'raw_material_stock.html'  
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    queryset = AddStockTmp.objects.filter(status=1) 

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewRawmaterialStockView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewRawmaterialStockView, self).get_context_data(*args, **kwargs) 


# Add stock view
class ViewCreatreStockView(LoggedInMixin, SuccessMessageMixin, CreateView):
    model = AddStockTmp
    template_name = 'add_stock.html'
    form_class = RawMaterialStockForm 
    success_url = reverse_lazy('manageStock')
    success_message = "%(stock_item)s Was Created Successfully"
    
    def get_success_url(self):
        return reverse('manageStock')

    def form_valid(self,form):
        
        if  AddStockTmp.objects.filter(stock_item=form.cleaned_data['stock_item']).exists():
            obj = AddStockTmp.objects.get(stock_item=form.cleaned_data['stock_item'])
            total = Decimal(obj.stock_kg_qty) + Decimal(form.cleaned_data['stock_kg_qty'])
            totalamount = Decimal(obj.price) + Decimal(form.cleaned_data['price'])
            AddStockTmp.objects.filter(stock_item=form.cleaned_data['stock_item']).update(stock_kg_qty=Decimal(total), price= Decimal(totalamount))        

            item = RawMaterialItem.objects.get(raw_item=form.cleaned_data['stock_item'])
            data = AddStockMaster(stock_item=item, stock_kg_qty = form.cleaned_data['stock_kg_qty'], price=form.cleaned_data['price'])
            data.save() 
            messages.success(self.request, "Stock Update Successfully")
            return HttpResponseRedirect(self.get_success_url())

        else:
            item = RawMaterialItem.objects.get(raw_item=form.cleaned_data['stock_item'])
            data = AddStockMaster(stock_item=item, stock_kg_qty = form.cleaned_data['stock_kg_qty'], price=form.cleaned_data['price'])
            data.save()    
           
            return super().form_valid(form)
             

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# Stock Detials ListView
class ViewStockDetilasView(LoggedInMixin, ListView):
    model = AddStockMaster
    template_name = 'stock_detilas.html'
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    def get_queryset(self, **kwargs):
        return AddStockMaster.objects.filter(stock_item=self.kwargs['stock_item_id'])

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewStockDetilasView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewStockDetilasView, self).get_context_data(*args, **kwargs)    


# Use stock update view
class ViewStockUseView(LoggedInMixin, SuccessMessageMixin, UpdateView):
    model = AddStockTmp
    template_name = 'use_stock.html'
    form_class = StockUseForm
    success_url = reverse_lazy('manageStock')
    success_message = "%(stock_item)s Was Update Successfully"


    def form_valid(self, form, **kwargs):
        obj = AddStockTmp.objects.get(id=self.kwargs['pk'])
             
        if Decimal(form.cleaned_data['kg_qty']) > Decimal(form.cleaned_data['stock_kg_qty']):
            messages.success(self.request, 'Your updated stock is greater than remaning stock? Not update this stock.')
            return HttpResponseRedirect(self.get_success_url())
        else:         
            total = Decimal(form.cleaned_data['stock_kg_qty']) - Decimal(form.cleaned_data['kg_qty']) 

            AddStockTmp.objects.filter(id=self.kwargs['pk']).update(stock_kg_qty = Decimal(total))
            sdata = UseStock(stock_item= obj.stock_item, use_kg_qty = form.cleaned_data['kg_qty'])
            sdata.save()
            messages.success(self.request, 'Stock Update Successfully')
            return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))	

# view stock use detilas
class ViewStockUseDetialsView(LoggedInMixin, ListView):
    model = UseStock
    template_name = 'use_stock_detials.html'
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    def get_queryset(self, **kwargs):
        return UseStock.objects.filter(stock_item=self.kwargs['stock_item_id'])

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewStockUseDetialsView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewStockUseDetialsView, self).get_context_data(*args, **kwargs)     

""" End raw material content """

# Show purchase stock list view   
class ViewPurchaseStockView(LoggedInMixin, ListView, FormView):
    model = AddStockMaster
    template_name = 'purchase_stock.html'
    form_class = StockReportForm
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    queryset = AddStockMaster.objects.filter(status=1)

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewPurchaseStockView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewPurchaseStockView, self).get_context_data(*args, **kwargs)    

# Purchase stock report (CSV and PDF)
class ViewPurchaseStockReportView(LoggedInMixin, CreateView):
  
    def post(self, request, *args, **kwargs):
        report_obj = ReportList.objects.get(id=request.POST['list_name'])
        # CSV Report
        if report_obj.name == 'csv':
            response = HttpResponse(content_type='text/csv')
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")
            response['Content-Disposition'] = 'attachment; filename="Stock_Purchase_'+ d1 +'.csv"'
            writer = csv.writer(response)

            if not request.POST['stock_item'] == '':
                if not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                    csv_data = AddStockMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), stock_item=request.POST['stock_item'], status=1)
                    writer.writerow(['Item Name', 'Stock Kg / Qty', 'Price', 'Purchase Date'])
                    for i in csv_data:
                        stock_list = [i.stock_item, i.stock_kg_qty, i.price, i.created_at]
                        writer.writerow(stock_list) 
                    return response                   
                else:
                    csv_data = AddStockMaster.objects.filter(status=1, stock_item=request.POST['stock_item'])
                    writer.writerow(['Item Name', 'Stock Kg / Qty', 'Price', 'Purchase Date'])
                    for i in csv_data:
                        stock_list = [i.stock_item, i.stock_kg_qty, i.price, i.created_at]
                        writer.writerow(stock_list) 
                    return response    
            elif not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                csv_data = AddStockMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']))
                writer.writerow(['Item Name', 'Stock Kg / Qty', 'Price', 'Purchase Date'])
                for i in csv_data:
                    stock_list = [i.stock_item, i.stock_kg_qty, i.price, i.created_at]
                    writer.writerow(stock_list) 
                return response                        
            else:
                csv_data = AddStockMaster.objects.filter(status=1)
                writer.writerow(['Item Name', 'Stock Kg / Qty', 'Price', 'Purchase Date'])
                for i in csv_data:
                    stock_list = [i.stock_item, i.stock_kg_qty, i.price, i.created_at]
                    writer.writerow(stock_list) 
                return response 
           
        # PDF Report   
        elif report_obj.name == 'pdf':

            if not request.POST['stock_item'] == '':
                if not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                    pdf_data = AddStockMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), stock_item=request.POST['stock_item'], status=1)
                    pdf = render_to_pdf('reports/purchase_stock_report.html' ,{'data':pdf_data})
                    return HttpResponse(pdf, content_type='application/pdf')
                else:
                    pdf_data = AddStockMaster.objects.filter(status=1, stock_item=request.POST['stock_item'])
                    pdf = render_to_pdf('reports/purchase_stock_report.html' ,{'data':pdf_data})
                    return HttpResponse(pdf, content_type='application/pdf')    
            elif not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                pdf_data = AddStockMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']))
                pdf = render_to_pdf('reports/purchase_stock_report.html' ,{'data':pdf_data})
                return HttpResponse(pdf, content_type='application/pdf')                        
            else:
                pdf_data = AddStockMaster.objects.filter(status=1)
                pdf = render_to_pdf('reports/purchase_stock_report.html' ,{'data':pdf_data})
                return HttpResponse(pdf, content_type='application/pdf')

    def get_context_data(self, *args, **kwargs):
        try:
            raise Http404("Report does not exist")
        except Http404:
            raise Http404("Report does not exist")	            

# Stock use View
class ViewUseStockView(LoggedInMixin, ListView, FormView):
    model = UseStock
    template_name = 'use_stock_report.html'
    form_class = StockReportForm
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    queryset = UseStock.objects.filter(status=1)

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewUseStockView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewUseStockView, self).get_context_data(*args, **kwargs)   


# Use stock report (CSV and PDF)
class ViewUseStockReportView(LoggedInMixin, CreateView):
  
    def post(self, request, *args, **kwargs):
        report_obj = ReportList.objects.get(id=request.POST['list_name'])
        # CSV Report
        if report_obj.name == 'csv':
            response = HttpResponse(content_type='text/csv')
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")
            response['Content-Disposition'] = 'attachment; filename="Stock_Purchase_'+ d1 +'.csv"'
            writer = csv.writer(response)

            if not request.POST['stock_item'] == '':
                if not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                    csv_data = UseStock.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), stock_item=request.POST['stock_item'], status=1).order_by('-created_at')
                    writer.writerow(['Item Name', ' Use Stock Kg / Qty', 'Stock Use Date'])
                    for i in csv_data:
                        stock_list = [i.stock_item, i.use_kg_qty, i.created_at]
                        writer.writerow(stock_list) 
                    return response                   
                else:
                    csv_data = UseStock.objects.filter(status=1, stock_item=request.POST['stock_item']).order_by('-created_at')
                    writer.writerow(['Item Name', ' Use Stock Kg / Qty', 'Stock Use Date'])
                    for i in csv_data:
                        stock_list = [i.stock_item, i.use_kg_qty, i.created_at]
                        writer.writerow(stock_list) 
                    return response    
            elif not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                csv_data = UseStock.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date'])).order_by('-created_at')
                writer.writerow(['Item Name', ' Use Stock Kg / Qty', 'Stock Use Date'])
                for i in csv_data:
                    stock_list = [i.stock_item, i.use_kg_qty, i.created_at]
                    writer.writerow(stock_list) 
                return response                        
            else:
                csv_data = UseStock.objects.filter(status=1).order_by('-created_at')
                writer.writerow(['Item Name', ' Use Stock Kg / Qty', 'Stock Use Date'])
                for i in csv_data:
                    stock_list = [i.stock_item, i.use_kg_qty, i.created_at]
                    writer.writerow(stock_list) 
                return response 
           
        # PDF Report   
        elif report_obj.name == 'pdf':

            if not request.POST['stock_item'] == '':
                if not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                    pdf_data = UseStock.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), stock_item=request.POST['stock_item'], status=1).order_by('-created_at')
                    pdf = render_to_pdf('reports/use_stock_report.html' ,{'data':pdf_data})
                    return HttpResponse(pdf, content_type='application/pdf')
                else:
                    pdf_data = UseStock.objects.filter(status=1, stock_item=request.POST['stock_item']).order_by('-created_at')
                    pdf = render_to_pdf('reports/use_stock_report.html' ,{'data':pdf_data})
                    return HttpResponse(pdf, content_type='application/pdf')    
            elif not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
                pdf_data = UseStock.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date'])).order_by('-created_at')
                pdf = render_to_pdf('reports/use_stock_report.html' ,{'data':pdf_data})
                return HttpResponse(pdf, content_type='application/pdf')                        
            else:
                pdf_data = UseStock.objects.filter(status=1).order_by('-created_at')
                pdf = render_to_pdf('reports/use_stock_report.html' ,{'data':pdf_data})
                return HttpResponse(pdf, content_type='application/pdf')

    def get_context_data(self, *args, **kwargs):
        try:
            raise Http404("Report does not exist")
        except Http404:
            raise Http404("Report does not exist")	   

''' Expenses content'''

class ViewManageExpenses(LoggedInMixin, ListView):
    model = ExpesesList
    template_name = 'view_expeses.html'
    ordering =  ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    def get_queryset(self, **kwargs):
        return ExpesesList.objects.filter(status=1)

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewManageExpenses, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewManageExpenses, self).get_context_data(*args, **kwargs)


class ViewCreateNewExpeses(LoggedInMixin, SuccessMessageMixin, CreateView):
    model = ExpesesList
    template_name = 'add_new_expeses.html'
    form_class = ExpesesForm
    success_url = reverse_lazy('manageExpenses')
    success_message = "%(expenses_name)s Was Created Successfully"

    def form_valid(self,form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class ViewExpesesUpdateView(LoggedInMixin, SuccessMessageMixin, UpdateView):
    model = ExpesesList
    template_name  = 'edit_expeses.html'
    form_class = ExpesesForm	
    success_url = reverse_lazy('manageExpenses')
    success_message = "%(expenses_name)s Was Update Successfully"

    def form_valid(self,form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))  

# Delete Expese
class ViewExpesesDeleteView(LoggedInMixin,RedirectView):
	url = '/polls/manageExpenses'

	def get_redirect_url(self, *args, **kwargs):
		del_id = kwargs['pk']
		ExpesesList.objects.filter(id=del_id).update(status=2)
		return super().get_redirect_url(*args, **kwargs) 

''' End Expeses content '''

''' paid Expeses content'''
class ViewPaidExpesesView(LoggedInMixin, ListView):
    model = ExpensesMaster
    template_name = 'view_paid_expeses.html'
    ordering =  ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    def get_queryset(self, **kwargs):
        return ExpensesMaster.objects.filter(status=1)

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewPaidExpesesView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewPaidExpesesView, self).get_context_data(*args, **kwargs)

class ViewCreateNewExpeses(LoggedInMixin, SuccessMessageMixin, CreateView):
    model = ExpensesMaster
    template_name = 'add_new_expeses.html'
    form_class = PaidExpesesForm
    success_url = reverse_lazy('paidExpeses')
    success_message = "%(expenses)s Was Created Successfully"

    def form_valid(self,form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# Stock use View
class ViewPaidExpesesReportView(LoggedInMixin, ListView, FormView):
    model = ExpensesMaster
    template_name = 'paid_expeses_report.html'
    form_class = DateWiseReport
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 1

    queryset = ExpensesMaster.objects.filter(status=1)

    def get_context_data(self, *args, **kwargs):
        try:
            return super(ViewPaidExpesesReportView, self).get_context_data(*args, **kwargs)
        except Http404:
            self.kwargs['page'] = 1
            return super(ViewPaidExpesesReportView, self).get_context_data(*args, **kwargs)  

class ViewExpesesReportView(LoggedInMixin, CreateView):
  
    def post(self, request, *args, **kwargs):
        # PDF Report      
        if not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
            pdf_data = ExpensesMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), status=1)
            pdf = render_to_pdf('reports/expeses.html' ,{'data':pdf_data})
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            pdf_data = ExpensesMaster.objects.filter(status=1).order_by('-created_at')
            pdf = render_to_pdf('reports/expeses.html' ,{'data':pdf_data})
            return HttpResponse(pdf, content_type='application/pdf')    
       

    def get_context_data(self, *args, **kwargs):
        try:
            raise Http404("Report does not exist")
        except Http404:
            raise Http404("Report does not exist")	   


class ViewIncomeAndgains(LoggedInMixin,ListView,  FormView):
    model = ExpensesMaster
    template_name='incomeandgains.html'
    form_class = DateWiseReport 
    ordering = ['-created_at'] 
    paginate_by = 10
   
    
    def get_context_data(self, *args, **kwargs):

        # Expeses List
        context = super(ViewIncomeAndgains, self).get_context_data(**kwargs)

        exp_list = ExpensesMaster.objects.filter(status=1)
        context['expenses_list'] = exp_list
      

        # Stock Expeses    
        stock_expeses = AddStockMaster.objects.filter(status=1)       
        context['stock_expeses_list'] = stock_expeses

        # Orders income   
        order_income = Orders.objects.all() 
        context['order_income_list'] = order_income

        return context


class ViewExpeseAndGainsReport(LoggedInMixin, CreateView):
  
    def post(self, request, *args, **kwargs):
        # PDF Report      
        if not request.POST['from_date'] == '' and not request.POST['to_date'] == '':
            stock_master_data = AddStockMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), status=1)
            exp_data = ExpensesMaster.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), status=1)
            order_data = Orders.objects.filter(created_at__range=(request.POST['from_date'],request.POST['to_date']), status=1) 
                     
            pdf = render_to_pdf('reports/expesesAndGensReport.html' ,{'stock_master_data':stock_master_data, 'exp_data':exp_data, 'order_data':order_data})
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            stock_master_data = AddStockMaster.objects.filter(status=1)
            exp_data = ExpensesMaster.objects.filter(status=1)
            order_data = Orders.objects.filter(status=1) 
                     
            pdf = render_to_pdf('reports/expesesAndGensReport.html' ,{'stock_master_data':stock_master_data , 'exp_data':exp_data, 'order_data':order_data})
            return HttpResponse(pdf, content_type='application/pdf')    
       

    def get_context_data(self, *args, **kwargs):
        try:
            raise Http404("Report does not exist")
        except Http404:
            raise Http404("Report does not exist")
            
''' end paid expensescontent '''