from . import views
from django.urls import path, re_path
from django.conf.urls import include, url

urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('changepass/', views.MyPasswordChangeView.as_view(), name='changepass'),
    path('changepassdone/', views.MyPasswordChangeDoneView.as_view(), name='chnagepassdone'),
    path('dashboard/', views.MyDashboardView.as_view(), name='dashboard'),

    # Menu Urls
    path('manageMenu', views.ShowMenuListView.as_view(), name='manageMenu'),
    path('createMenu', views.CreateMenuView.as_view(), name='createMenu'),
    path('editMenu/<str:slug>', views.MenuUpdateView.as_view(), name='editMenu'),
    path('deleteMenu/<str:slug>', views.DeleteMenuView.as_view(), name='deleteMenu'),
    path('createOrder', views.CreateOrderView.as_view(), name='createOrder'),
    path('manageOrder', views.ManageOrderView.as_view(), name='manageOrder'),
    path('showOrder', views.ShowOrderListView.as_view(), name='show'),
    path('orderPrint', views.ShowOrderPrintView.as_view(), name='orderPrint'),

    # Bills Url
    path('viewBills', views.ShowBillsListView.as_view(), name='viewBills'),
    path(r'^viewOrder/(?P<invoice_no>\d+)$', views.ViewOrderListView.as_view(), name='viewOrder'),
    path('viewOrderDetails', views.ViewOrderDetialsView.as_view(), name='viewOrderDetails'),
    path(r'^dateWiseDetials/(?P<pk>\d+)$', views.ViewDateWiseOrderDetialsView.as_view(), name='dateWiseDetials'),
    path('orderReportPDF/<int:pk>', views.ViewOrderPDFReportView.as_view(), name='orderReportPDF'),
    path('orderReportCSV/<int:pk>', views.ViewOrderCSVReportView.as_view(), name='orderReportCSV'),
    path('receiptBill/<int:invoice_no>', views.ViewRecieptBillView.as_view(), name='receiptBill'),

    # Data visualization url
    path('barCharts', views.ViewBarVisualizationView.as_view(), name='barCharts'),
    path('lineCharts', views.ViewLineVisualizationView.as_view(), name='lineCharts'),
    path('pieCharts', views.ViewPieVisualizationView.as_view() ,name='pieCharts'),
    path('api/chart/data', views.ChartData.as_view()),

    # Filter data visualization
    path('barChartsFilter', views.ViewBarChartsFilterView.as_view(), name='barChartsFilter'),
    path('lineChartsFilter', views.ViewLineChartsFilterView.as_view(), name='lineChartsFilter'),
    path('pieChartsFilter', views.ViewPieChartFilterView.as_view(), name='pieChartsFilter'),
    path('api/chart/filterdata', views.ChartDataFilter.as_view()),

    # Raw material url
    path('manageRawMaterial', views.ViewManageRawMaterialView.as_view(), name='manageRawMaterial'), 
    path('createRawMaterial', views.ViewCreateRawMaterialView.as_view(), name='createRawMaterial'), 
    path('editRawMaterial/<str:slug>', views.ViewRawMaterialUpdateView.as_view(), name='editRawMaterial'),  
    path('deleteRawmaterial/<int:pk>', views.ViewRawMaterialDeleteView.as_view(), name='deleteRawmaterial'),

    # Stock url
    path('manageStock', views.ViewRawmaterialStockView.as_view(), name='manageStock'),
    path('addStock', views.ViewCreatreStockView.as_view(), name='addStock'),
    path(r'^stockDetials/(?P<stock_item_id>\d+)$', views.ViewStockDetilasView.as_view(), name='stockDetials'),
    path(r'^useStock/(?P<pk>\d+)$', views.ViewStockUseView.as_view(), name='useStock'),
    path(r'^stockUse/(?P<stock_item_id>\d+)$', views.ViewStockUseDetialsView.as_view(), name='stockUse'),
    path('purchaseStock', views.ViewPurchaseStockView.as_view(), name='purchaseStock'),
    path('StockReport', views.ViewPurchaseStockReportView.as_view(), name='StockReport'),
    path('useStock', views.ViewUseStockView.as_view(), name='useStock'),
    path('useStockReport', views.ViewUseStockReportView.as_view(), name='useStockReport'),

    # ManageExpenses url
    path('manageExpenses', views.ViewManageExpenses.as_view(), name='manageExpenses'),
    path('createExpeses', views.ViewCreateNewExpeses.as_view(), name='createExpeses'),
    path(r'^editexpeses/(?P<pk>\d+)$', views.ViewExpesesUpdateView.as_view(), name='editexpeses'),
    path(r'^deleteexpeses/(?P<pk>\d+)$', views.ViewExpesesDeleteView.as_view(), name='deleteexpeses'),

    # manage paid expeses url
    path('paidExpeses', views.ViewPaidExpesesView.as_view(), name='paidExpeses'),
    path('addExpeses', views.ViewCreateNewExpeses.as_view(), name='addExpeses'),
    path('paidExpesesReport', views.ViewPaidExpesesReportView.as_view(), name='paidExpesesReport'),
    path('expensesreport', views.ViewExpesesReportView.as_view(), name='expensesreport'),  
    path('incomeAndGains', views.ViewIncomeAndgains.as_view(), name='incomeAndGains'),
    path('expensesAndGainsReport', views.ViewExpeseAndGainsReport.as_view(), name='expensesAndGainsReport'),
    
]

