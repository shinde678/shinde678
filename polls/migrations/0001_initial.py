# Generated by Django 3.2.7 on 2021-11-08 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExpesesList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expenses_name', models.CharField(max_length=200, null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ExpesesList',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_no', models.IntegerField(null=True)),
                ('invoice_item_quantity', models.FloatField(null=True)),
                ('invoice_item_final_total', models.FloatField(null=True)),
                ('invoice_date', models.DateField()),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'Invoice',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu_name', models.CharField(max_length=50, null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'db_table': 'Menu',
            },
        ),
        migrations.CreateModel(
            name='OrdersMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('master_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'OrdersMaster',
            },
        ),
        migrations.CreateModel(
            name='RawMaterialItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_item', models.CharField(max_length=50, null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'db_table': 'RawMaterialItem',
            },
        ),
        migrations.CreateModel(
            name='ReportList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ReportList',
            },
        ),
        migrations.CreateModel(
            name='UseStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_kg_qty', models.FloatField(null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('stock_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.rawmaterialitem')),
            ],
            options={
                'db_table': 'UseStock',
            },
        ),
        migrations.CreateModel(
            name='StockReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.reportlist')),
                ('stock_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.rawmaterialitem')),
            ],
            options={
                'db_table': 'StockReport',
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_no', models.IntegerField(null=True)),
                ('item_price', models.FloatField(null=True)),
                ('item_qty', models.FloatField(default=0, null=True)),
                ('item_total', models.FloatField(null=True)),
                ('item_date', models.DateField()),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('item_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.menu')),
            ],
            options={
                'db_table': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='ExpensesMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expenses_amount', models.FloatField(null=True)),
                ('desc', models.CharField(max_length=300, null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expenses', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.expeseslist')),
            ],
            options={
                'db_table': 'ExpensesMaster',
            },
        ),
        migrations.CreateModel(
            name='AddStockTmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_kg_qty', models.FloatField(null=True)),
                ('price', models.FloatField(null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('stock_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.rawmaterialitem')),
            ],
        ),
        migrations.CreateModel(
            name='AddStockMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_kg_qty', models.FloatField(null=True)),
                ('price', models.FloatField(null=True)),
                ('status', models.IntegerField(default=1, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('stock_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.rawmaterialitem')),
            ],
        ),
    ]
