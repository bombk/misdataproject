from django.contrib import admin
from .models import (
    Branch, CustomerCategory, ServiceType, TransactionType,TransactionRange, 
    InstrumentType, GeographicalLocation, ChannelUsed,
    CustomerData, TransactionData, DataUploadLog,TotalUser, TotalTransaction
)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['branch_code', 'branch_name']
    search_fields = ['branch_code', 'branch_name']

@admin.register(CustomerCategory)
class CustomerCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']
    search_fields = ['category_name']

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['service_name']
    search_fields = ['service_name']
@admin.register(TransactionRange)
class TransactionRangeAdmin(admin.ModelAdmin):
    list_display = ['range_name']
    search_fields = ['range_name']

@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ['transaction_type_name']
    search_fields = ['transaction_type_name']

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ['instrument_type_name']
    search_fields = ['instrument_type_name']

@admin.register(GeographicalLocation)
class GeographicalLocationAdmin(admin.ModelAdmin):
    list_display = ['location_name']
    search_fields = ['location_name']

@admin.register(ChannelUsed)
class ChannelUsedAdmin(admin.ModelAdmin):
    list_display = ['channel_name']
    search_fields = ['channel_name']

@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = ['branch_code', 'customer_category', 'service_type', 'status', 'number_of_customers', 'month_year']
    list_filter = ['status', 'month_year', 'customer_category', 'service_type']
    search_fields = ['branch_code__branch_code', 'branch_code__branch_name']
    date_hierarchy = 'month_year'

@admin.register(TransactionData)
class TransactionDataAdmin(admin.ModelAdmin):
    list_display = ['range_of_transactions', 'form_of_instrument', 'type_of_transaction', 'number_of_transactions', 'amount', 'month_year']
    list_filter = ['month_year', 'form_of_instrument', 'type_of_transaction', 'geographical_location', 'channel_used']
    search_fields = ['range_of_transactions']
    date_hierarchy = 'month_year'

@admin.register(DataUploadLog)
class DataUploadLogAdmin(admin.ModelAdmin):
    list_display = ['upload_date', 'month_year', 'data_type', 'file_name', 'records_uploaded', 'status']
    list_filter = ['status', 'data_type', 'month_year']
    search_fields = ['file_name']
    date_hierarchy = 'upload_date'
    readonly_fields = ['upload_date']

@admin.register(TotalUser)
class TotalUserAdmin(admin.ModelAdmin):
    list_display = ['id','fiscal_year','month_year', 'service_type', 'status', 'count', 'created_at', 'updated_at']
    list_filter = ['month_year']
    search_fields = ['month_year']
    date_hierarchy = 'month_year'

@admin.register(TotalTransaction)
class TotalTransactionAdmin(admin.ModelAdmin):
    list_display = ['id','fiscal_year', 'month_year', 'transaction_range', 'type_of_transaction','form_of_instrument', 'geographical_location', 'channel_used', 'number_of_transactions','amount', 'created_at', 'updated_at']
    list_filter = ['month_year']
    search_fields = ['month_year']
    date_hierarchy = 'month_year'
