from django.contrib import admin
from .models import *

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id','menu_name','status','created_at','updated_at']

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
	list_display = ['id','invoice_no','item_name','item_price','item_qty','item_total','status','created_at','updated_at']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id','invoice_no','invoice_item_quantity','invoice_item_final_total','invoice_date','status','created_at','updated_at']

@admin.register(OrdersMaster)
class OrdersMasterAdmin(admin.ModelAdmin):
    list_display = ['id','master_date','created_at','updated_at']


admin.site.register(RawMaterialItem)
admin.site.register(AddStockTmp)
admin.site.register(ReportList)
admin.site.register(ExpesesList)
admin.site.register(ExpensesMaster)
