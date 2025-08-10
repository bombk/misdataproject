from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Branch(models.Model):
    branch_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.branch_code} - {self.branch_name}"
    
    class Meta:
        verbose_name_plural = "Branches"

class CustomerCategory(models.Model):
    category_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural = "Customer Categories"

class ServiceType(models.Model):
    service_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.service_name
    
    class Meta:
        verbose_name_plural = "Service Types"

class TransactionRange(models.Model):
    range_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.range_name
    
    class Meta:
        verbose_name_plural = "Transaction Ranges"

class TransactionType(models.Model):
    transaction_type_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.transaction_type_name
    
    class Meta:
        verbose_name_plural = "Transaction Types"

class InstrumentType(models.Model):
    instrument_type_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.instrument_type_name
    
    class Meta:
        verbose_name_plural = "Instrument Types"

class GeographicalLocation(models.Model):
    location_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.location_name
    
    class Meta:
        verbose_name_plural = "Geographical Locations"

class ChannelUsed(models.Model):
    channel_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.channel_name
    
    class Meta:
        verbose_name_plural = "Channels Used"

class CustomerData(models.Model):
    branch_code = models.ForeignKey(Branch, on_delete=models.CASCADE)
    customer_category = models.ForeignKey(CustomerCategory, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')])
    number_of_customers = models.IntegerField(validators=[MinValueValidator(0)])
    month_year = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.branch_code} - {self.customer_category} - {self.month_year}"
    
    class Meta:
        verbose_name_plural = "Customer Data"
        unique_together = ['branch_code', 'customer_category', 'service_type', 'status', 'month_year']

class TransactionData(models.Model):
    month_year = models.DateField()
    range_of_transactions = models.CharField(max_length=100)
    form_of_instrument = models.ForeignKey(InstrumentType, on_delete=models.CASCADE)
    type_of_transaction = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    geographical_location = models.ForeignKey(GeographicalLocation, on_delete=models.CASCADE)
    channel_used = models.ForeignKey(ChannelUsed, on_delete=models.CASCADE)
    number_of_transactions = models.IntegerField(validators=[MinValueValidator(0)])
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.range_of_transactions} - {self.month_year}"
    
    class Meta:
        verbose_name_plural = "Transaction Data"
        unique_together = ['month_year', 'range_of_transactions', 'form_of_instrument', 'type_of_transaction', 'geographical_location', 'channel_used']

class DataUploadLog(models.Model):
    upload_date = models.DateTimeField(auto_now_add=True)
    month_year = models.DateField()
    data_type = models.CharField(max_length=20, choices=[('CUSTOMER', 'Customer Data'), ('TRANSACTION', 'Transaction Data')])
    file_name = models.CharField(max_length=255)
    records_uploaded = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('PARTIAL', 'Partial')])
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.data_type} - {self.month_year} - {self.status}"
    
    class Meta:
        verbose_name_plural = "Data Upload Logs"


class TotalUser(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    fiscal_year = models.CharField(max_length=10)
    month_year = models.DateField()
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_type} - {self.status} ({self.month_year})"


class TotalTransaction(models.Model):
    fiscal_year = models.CharField(max_length=10)
    month_year = models.DateField()
    transaction_range = models.ForeignKey(TransactionRange, on_delete=models.CASCADE)
    type_of_transaction = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    form_of_instrument = models.ForeignKey(InstrumentType, on_delete=models.CASCADE)
    geographical_location = models.ForeignKey(GeographicalLocation, on_delete=models.CASCADE)
    channel_used = models.ForeignKey(ChannelUsed, on_delete=models.CASCADE)
    number_of_transactions = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_range} - {self.type_of_transaction} - {self.month_year}"