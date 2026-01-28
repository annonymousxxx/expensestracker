from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import Expense
from .forms import ExpenseForm

# DASHBOARD
@login_required
def dashboard(request):
    # Get current month date range
    today = datetime.now().date()
    first_day = today.replace(day=1)
    
    # Calculate monthly stats
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__gte=first_day,
        date__lte=today
    )
    
    # Total spent this month
    total_spent = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Category breakdown
    category_stats = monthly_expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Biggest category
    top_category = category_stats.first() if category_stats else None
    
    # Last 6 months trend data
    months_data = []
    for i in range(5, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        if i == 0:
            month_end = today
        else:
            next_month = month_start.replace(day=28) + timedelta(days=4)
            month_end = next_month - timedelta(days=next_month.day)
        
        month_total = Expense.objects.filter(
            user=request.user,
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        months_data.append({
            'month': month_start.strftime('%b'),
            'total': float(month_total)
        })
    
    # Recent expenses
    recent_expenses = monthly_expenses.order_by('-date')[:5]
    
    context = {
        'total_spent': total_spent,
        'top_category': top_category,
        'category_stats': category_stats,
        'months_data': months_data,
        'recent_expenses': recent_expenses,
        'current_month': first_day.strftime('%B %Y'),
    }
    return render(request, 'expenses/pages/dashboard.html', context)

# READ
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/pages/expenses_list.html', {'expenses': expenses})

# CREATE
@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/pages/expenses_form.html', {'form': form, 'title': 'Add Expense'})

# UPDATE
@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/pages/expenses_form.html', {'form': form, 'title': 'Edit Expense'})

# DELETE
@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/pages/expenses_confirm_delete.html', {'expense': expense})

# DETAIL
@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'expenses/pages/expenses_detail.html', {'expense': expense})
