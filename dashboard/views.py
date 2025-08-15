from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.db import models
from django.db import transaction
from django.core.serializers import serialize
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms.models import model_to_dict
import csv
import io
import json
from django.utils import timezone
from datetime import timedelta
from .models import (
    Branch, CustomerCategory, ServiceType,TransactionRange, TransactionType,
    InstrumentType, GeographicalLocation, ChannelUsed,
    CustomerData, TransactionData, DataUploadLog, TotalUser, TotalTransaction
)

# @login_required
# def dashboard_home(request):
#     # Get the latest month_year
#     latest_month_year = TotalUser.objects.latest('month_year').month_year

#     # Filter all rows with that month_year
#     latest_records = TotalUser.objects.filter(month_year=latest_month_year)

#     # Convert queryset to list of dicts
#     data = [model_to_dict(record) for record in latest_records]

#     return JsonResponse({
#         'latest_month_year': latest_month_year.strftime('%Y-%m'),
#         'records': data
#     })
def dashboard_home(request):
    # ======== Users Data ========
    latest_user_month = TotalUser.objects.latest('month_year').month_year

    user_aggregated = (
        TotalUser.objects
        .filter(month_year=latest_user_month)
        .values('service_type__service_name', 'status')
        .annotate(total_count=Sum('count'))
    )

    user_cards = {}
    for record in user_aggregated:
        service_name = record['service_type__service_name']
        status = record['status']
        total_count = record['total_count']
        if service_name not in user_cards:
            user_cards[service_name] = {'active': 0, 'inactive': 0}
        user_cards[service_name][status] = total_count

    for service_name, counts in user_cards.items():
        counts['total'] = counts['active'] + counts['inactive']

    # ======== Transactions Data ========
    latest_tx_month = TotalTransaction.objects.latest('month_year').month_year

    tx_aggregated = (
        TotalTransaction.objects
        .filter(month_year=latest_tx_month)
        .values('form_of_instrument__instrument_type_name')
        .annotate(
            total_transactions=Sum('number_of_transactions'),
            total_amount=Sum('amount')
        )
    )

    transaction_cards = {}
    for record in tx_aggregated:
        instrument_name = record['form_of_instrument__instrument_type_name']
        transaction_cards[instrument_name] = {
            'total_transactions': record['total_transactions'],
            'total_amount': record['total_amount']
        }

    return render(request, 'dashboard/index.html', {
        'latest_user_month': latest_user_month.strftime('%Y-%m'),
        'user_cards': user_cards,
        'latest_tx_month': latest_tx_month.strftime('%Y-%m'),
        'transaction_cards': transaction_cards
    })
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

def total_user_list(request):
    status_filter = request.GET.get('status')

    queryset = TotalUser.objects.select_related('service_type').order_by('-month_year')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/total_user_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter
    })
def total_transaction_list(request):
    transaction_type_filter = request.GET.get('transaction_type')

    queryset = TotalTransaction.objects.select_related(
        'transaction_range', 'type_of_transaction',
        'form_of_instrument', 'geographical_location', 'channel_used'
    ).order_by('-month_year')

    if transaction_type_filter:
        queryset = queryset.filter(type_of_transaction_id=transaction_type_filter)

    paginator = Paginator(queryset, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    transaction_types = TransactionType.objects.all()

    return render(request, 'dashboard/total_transaction_list.html', {
        'page_obj': page_obj,
        'transaction_type_filter': transaction_type_filter,
        'transaction_types': transaction_types
    })

def total_user_summary(request):
    fiscal_year = request.GET.get('fiscal_year')
    month_year = request.GET.get('month_year')

    queryset = TotalUser.objects.all()

    if fiscal_year:
        queryset = queryset.filter(fiscal_year=fiscal_year)

    if month_year:
        # Expecting month_year in 'YYYY-MM' format, convert to date filtering
        from datetime import datetime
        try:
            date_obj = datetime.strptime(month_year, '%Y-%m').date()
            # Filter by month and year
            queryset = queryset.filter(month_year__year=date_obj.year, month_year__month=date_obj.month)
        except ValueError:
            pass  # invalid format, ignore filter or handle error as you want

    # Group and aggregate count of active and inactive by service_type and month_year
    summary = (
        queryset
        .values('service_type__service_name', 'month_year')
        .annotate(
            active_count=Sum('count', filter=models.Q(status='active')),
            inactive_count=Sum('count', filter=models.Q(status='inactive'))
        )
        .order_by('month_year', 'service_type__service_name')
    )

    paginator = Paginator(summary, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'fiscal_year': fiscal_year,
        'month_year': month_year,
    }

    return render(request, 'dashboard/total_user_summary.html', context)

def total_transaction_summary(request):
    # Filters from GET
    
    filters = {}
    q = Q()

    transaction_range = request.GET.get('transaction_range')
    if transaction_range:
        q &= Q(transaction_range_id=transaction_range)

    type_of_transaction = request.GET.get('type_of_transaction')
    if type_of_transaction:
        q &= Q(type_of_transaction_id=type_of_transaction)

    form_of_instrument = request.GET.get('form_of_instrument')
    if form_of_instrument:
        q &= Q(form_of_instrument_id=form_of_instrument)

    geographical_location = request.GET.get('geographical_location')
    if geographical_location:
        q &= Q(geographical_location_id=geographical_location)

    channel_used = request.GET.get('channel_used')
    if channel_used:
        q &= Q(channel_used_id=channel_used)

    # Filter by number_of_transactions range if provided
    min_num = request.GET.get('min_transactions')
    if min_num:
        try:
            min_num = int(min_num)
            q &= Q(number_of_transactions__gte=min_num)
        except ValueError:
            pass

    max_num = request.GET.get('max_transactions')
    if max_num:
        try:
            max_num = int(max_num)
            q &= Q(number_of_transactions__lte=max_num)
        except ValueError:
            pass

    qs = TotalTransaction.objects.filter(q).order_by('-month_year')

    # Aggregate sums
    aggregates = qs.aggregate(
        total_transactions=Sum('number_of_transactions'),
        total_amount=Sum('amount'),
    )

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass filter dropdown options for the template
    context = {
        'page_obj': page_obj,
        'aggregates': aggregates,
        'transaction_ranges': TransactionRange.objects.all(),
        'transaction_types': TransactionType.objects.all(),
        'instrument_types': InstrumentType.objects.all(),
        'geographical_locations': GeographicalLocation.objects.all(),
        'channels_used': ChannelUsed.objects.all(),
        # Keep filters to retain form selections
        'filter_values': {
            'transaction_range': transaction_range,
            'type_of_transaction': type_of_transaction,
            'form_of_instrument': form_of_instrument,
            'geographical_location': geographical_location,
            'channel_used': channel_used,
            'min_transactions': min_num if min_num else '',
            'max_transactions': max_num if max_num else '',
        }
    }

    return render(request, 'dashboard/total_transaction_summary.html', context)


