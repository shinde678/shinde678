from __future__ import unicode_literals
from django.db import models
from .slugs import *
from django.db.models.signals import pre_save


# Add farmer model
class Menu(models.Model):
	menu_name = models.CharField(max_length=50, null=True)
	status = models.IntegerField(default=1,null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	slug = models.SlugField(unique=True, null=True, blank=True)

	def __str__(self):
		return self.menu_name	

	class Meta:
		db_table = "Menu"

def pre_save_menu(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = unique_slug_generator_menuname(instance)

pre_save.connect(pre_save_menu, sender = Menu)

# Invoice Model
class Invoice(models.Model):
	invoice_no = models.IntegerField(null=True)
	invoice_item_quantity = models.FloatField(null=True)
	invoice_item_final_total = models.FloatField(null=True)
	invoice_date = models.DateField()
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		db_table = "Invoice"

# Orders Model
class Orders(models.Model):
	invoice_no = models.IntegerField(null=True)
	item_name = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True)
	item_price = models.FloatField(null=True)
	item_qty = models.FloatField(null=True, default=0)
	item_total = models.FloatField(null=True)
	item_date = models.DateField()
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


	def __int__(self):
		return "%d"(self.id	)

	class Meta:
		db_table = "Orders"
	

# Ordersmaster Model
class OrdersMaster(models.Model):
	master_date = models.DateField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __int__(self):
		return "%d"(self.id)

	class Meta:
		db_table = "OrdersMaster"


class RawMaterialItem(models.Model):
	raw_item = models.CharField(max_length=50, null=True)
	status = models.IntegerField(default=1,null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	slug = models.SlugField(unique=True, null=True, blank=True)

	def __str__(self):
		return self.raw_item
		

	class Meta:
		db_table = "RawMaterialItem"

def pre_save_rawmaterial(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = unique_slug_generator_rawitem(instance)

pre_save.connect(pre_save_rawmaterial, sender = RawMaterialItem)


class AddStockTmp(models.Model):
	stock_item = models.ForeignKey(RawMaterialItem,  on_delete=models.CASCADE, null=True)
	stock_kg_qty = models.FloatField(null=True)
	price = models.FloatField(null=True)
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now=True)

	def __str__(self):
		return self.stock_item
	

class AddStockMaster(models.Model):
	stock_item = models.ForeignKey(RawMaterialItem,  on_delete=models.CASCADE, null=True)
	stock_kg_qty = models.FloatField(null=True)
	price = models.FloatField(null=True)
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now=True)
	

class UseStock(models.Model):
	stock_item = models.ForeignKey(RawMaterialItem, on_delete=models.CASCADE, null=True)
	use_kg_qty = models.FloatField(null=True)
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now=True)

	class Meta:
		db_table = "UseStock"


# Report list model (create manunal report type)
class ReportList(models.Model):
	name = models.CharField(max_length=200, null=True)
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	class Meta:
		db_table = "ReportList"	

class StockReport(models.Model):
	stock_item = models.ForeignKey(RawMaterialItem,  on_delete=models.CASCADE, null=True)
	list_name = models.ForeignKey(ReportList, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

	class Meta:
		db_table = 	"StockReport"


class ExpesesList(models.Model):
	expenses_name = models.CharField(max_length=200, null=True)
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.expenses_name

	class Meta:
		db_table = 	"ExpesesList"

class ExpensesMaster(models.Model):
	expenses = models.ForeignKey(ExpesesList,  on_delete=models.CASCADE, null=True)
	expenses_amount = models.FloatField(null=True)
	desc = models.CharField(max_length=300, null=True)
	status = models.IntegerField(default=1, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.expenses

	class Meta:
		db_table = 	"ExpensesMaster"
