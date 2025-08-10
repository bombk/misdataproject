from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.db import transaction
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import csv
import io
import json
from .models import (
    Branch, CustomerCategory, ServiceType, TransactionType,
    InstrumentType, GeographicalLocation, ChannelUsed,
    CustomerData, TransactionData, DataUploadLog
)

@login_required
def dashboard_home(request):
    """Main dashboard view with summary statistics"""
    context = {
        'total_branches': Branch.objects.count(),
        'total_customer_records': CustomerData.objects.count(),
        'total_transaction_records': TransactionData.objects.count(),
        'recent_uploads': DataUploadLog.objects.order_by('-upload_date')[:5],
    }
    return render(request, 'dashboard/index.html', context)
@login_required
def master_parameters(request):
    """View for managing master parameters"""
    context = {
        'branches': Branch.objects.all(),
        'customer_categories': CustomerCategory.objects.all(),
        'service_types': ServiceType.objects.all(),
        'transaction_types': TransactionType.objects.all(),
        'instrument_types': InstrumentType.objects.all(),
        'geographical_locations': GeographicalLocation.objects.all(),
        'channels_used': ChannelUsed.objects.all(),
    }
    return render(request, 'dashboard/master_parameters.html', context)
@login_required
def data_upload(request):
    """View for uploading data files"""
    if request.method == 'POST':
        data_type = request.POST.get('data_type')
        month_year = request.POST.get('month_year')
        uploaded_file = request.FILES.get('data_file')
        
        if not all([data_type, month_year, uploaded_file]):
            messages.error(request, 'All fields are required.')
            return redirect('data_upload')
        
        try:
            month_year_date = datetime.strptime(month_year, '%Y-%m').date()
            
            if data_type == 'CUSTOMER':
                result = process_customer_data(uploaded_file, month_year_date)
            elif data_type == 'TRANSACTION':
                result = process_transaction_data(uploaded_file, month_year_date)
            else:
                messages.error(request, 'Invalid data type.')
                return redirect('data_upload')
            
            # Log the upload
            DataUploadLog.objects.create(
                month_year=month_year_date,
                data_type=data_type,
                file_name=uploaded_file.name,
                records_uploaded=result['records_uploaded'],
                status=result['status'],
                error_message=result.get('error_message', '')
            )
            
            if result['status'] == 'SUCCESS':
                messages.success(request, f"Successfully uploaded {result['records_uploaded']} records.")
            else:
                messages.error(request, f"Upload failed: {result.get('error_message', 'Unknown error')}")
                
        except ValueError:
            messages.error(request, 'Invalid date format. Use YYYY-MM.')
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')
        
        return redirect('data_upload')
    
    return render(request, 'dashboard/data_upload.html')
@login_required
def data_tables(request):
    """View for displaying data tables"""
    data_type = request.GET.get('type', 'customer')
    
    if data_type == 'customer':
        data = CustomerData.objects.select_related(
            'branch_code', 'customer_category', 'service_type'
        ).order_by('-month_year', 'branch_code')
        template = 'dashboard/customer_data_table.html'
    else:
        data = TransactionData.objects.select_related(
            'form_of_instrument', 'type_of_transaction', 
            'geographical_location', 'channel_used'
        ).order_by('-month_year', 'range_of_transactions')
        template = 'dashboard/transaction_data_table.html'
    
    paginator = Paginator(data, 25)  # Show 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'data_type': data_type,
    }
    return render(request, template, context)

def process_customer_data(uploaded_file, month_year):
    """Process uploaded customer data CSV file"""
    try:
        file_data = uploaded_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(file_data))
        
        records_uploaded = 0
        
        with transaction.atomic():
            for row in csv_data:
                # Create or get related objects
                branch, _ = Branch.objects.get_or_create(
                    branch_code=row['Branch code'],
                    defaults={'branch_name': row['Branch name']}
                )
                
                category, _ = CustomerCategory.objects.get_or_create(
                    category_name=row['Categorization of customers']
                )
                
                service, _ = ServiceType.objects.get_or_create(
                    service_name=row['Mobile Banking']
                )
                
                # Create customer data record
                CustomerData.objects.update_or_create(
                    branch_code=branch,
                    customer_category=category,
                    service_type=service,
                    status=row['Status'].upper(),
                    month_year=month_year,
                    defaults={
                        'number_of_customers': int(row['Number of customers'])
                    }
                )
                records_uploaded += 1
        
        return {'status': 'SUCCESS', 'records_uploaded': records_uploaded}
    
    except Exception as e:
        return {'status': 'FAILED', 'records_uploaded': 0, 'error_message': str(e)}

def process_transaction_data(uploaded_file, month_year):
    """Process uploaded transaction data CSV file"""
    try:
        file_data = uploaded_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(file_data))
        
        records_uploaded = 0
        
        with transaction.atomic():
            for row in csv_data:
                # Create or get related objects
                instrument, _ = InstrumentType.objects.get_or_create(
                    instrument_type_name=row['Form of instrument']
                )
                
                trans_type, _ = TransactionType.objects.get_or_create(
                    transaction_type_name=row['Type of transaction']
                )
                
                location, _ = GeographicalLocation.objects.get_or_create(
                    location_name=row['Geographical location']
                )
                
                channel, _ = ChannelUsed.objects.get_or_create(
                    channel_name=row['Channel used']
                )
                
                # Create transaction data record
                TransactionData.objects.update_or_create(
                    month_year=month_year,
                    range_of_transactions=row['Range of transactions'],
                    form_of_instrument=instrument,
                    type_of_transaction=trans_type,
                    geographical_location=location,
                    channel_used=channel,
                    defaults={
                        'number_of_transactions': int(row['Number of transactions']),
                        'amount': float(row['Amount'])
                    }
                )
                records_uploaded += 1
        
        return {'status': 'SUCCESS', 'records_uploaded': records_uploaded}
    
    except Exception as e:
        return {'status': 'FAILED', 'records_uploaded': 0, 'error_message': str(e)}

@csrf_exempt
def api_dashboard_data(request):
    """API endpoint for dashboard charts data"""
    if request.method == 'GET':
        # Customer data by status
        customer_status_data = CustomerData.objects.values('status').annotate(
            total=Sum('number_of_customers')
        )
        
        # Transaction data by type
        transaction_type_data = TransactionData.objects.values(
            'type_of_transaction__transaction_type_name'
        ).annotate(
            total_amount=Sum('amount'),
            total_count=Sum('number_of_transactions')
        )
        
        # Monthly trends
        monthly_customer_data = CustomerData.objects.values('month_year').annotate(
            total_customers=Sum('number_of_customers')
        ).order_by('month_year')
        
        monthly_transaction_data = TransactionData.objects.values('month_year').annotate(
            total_amount=Sum('amount'),
            total_transactions=Sum('number_of_transactions')
        ).order_by('month_year')
        
        data = {
            'customer_status': list(customer_status_data),
            'transaction_types': list(transaction_type_data),
            'monthly_customers': list(monthly_customer_data),
            'monthly_transactions': list(monthly_transaction_data),
        }
        
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(f"Attempting login for user: {username}")
        if user is None:
            print("Authentication failed.")
        else:
            print("Authentication successful.")
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')  # your SB Admin login template
@login_required
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')