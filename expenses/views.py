from django.http import HttpResponse
from .models import Expense, Category, Budget
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .forms import BudgetForm, ExpenseForm, CategoryForm
from django.db.models import Sum
from django.views.decorators.http import require_POST



@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            messages.success(
                request,
                "Expense added successfully!"
            )
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    if request.POST.get("source") == "transactions":
        return redirect("transactions")
    return redirect("dashboard")
        

@login_required
def home(request):
    expenses = Expense.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)

    search = request.GET.get("search")
    if search:
        expenses = expenses.filter(title__icontains=search)

    total = sum(expense.price for expense in expenses)

    current_month = timezone.now().date().replace(day=1)
    budgets = Budget.objects.filter(user=request.user, month=current_month)

    budget_status = []
    for budget in budgets:
        spent = budget.spent
        remaining = budget.remaining
        percentage = budget.percentage
        
        budget_status.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
        })
        if percentage >= 100:
            messages.error(request, f"🚨 Budget'{budget.category.name}' limit has ended!")
        elif percentage >= 80:
            messages.warning(request, f"⚠️ Warning!'{budget.category.name}' {percentage}% has been used up!")
    
    category_data = expenses.values('category__name').annotate(total=Sum('price'))
    category_names = [item['category__name'] or 'Without a category' for item in category_data]
    category_amounts = [item['total'] for item in category_data]

    monthly_data = []
    for i in range(6):
        month = timezone.now().date().replace(day=1) - timezone.timedelta(days=30*i)
        monthly_total = expenses.filter(
            date__year=month.year,
            date__month=month.month
        ).aggregate(total=Sum('price'))['total'] or 0
        monthly_data.append({
            'month': month.strftime('%B %Y'),
            'total': monthly_total,
        })
    monthly_data.reverse()
    monthly_labels = [item['month'] for item in monthly_data]
    monthly_totals = [item['total'] for item in monthly_data]

    return render(request, 'expenses/home.html', {
        'expenses': expenses,
        'categories': categories,
        'total': total,
        'budgets': budgets,
        'budget_status': budget_status,
        'category_names': category_names,
        'category_amounts': category_amounts,
        'monthly_labels': monthly_labels,
        'monthly_totals': monthly_totals,
    })



@login_required
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()

            messages.success(
                request,
                f"Category '{category.name}' added successfully!"
            )
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    return redirect("categories")


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(
        Category,
        id=category_id,
        user=request.user,
    )

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            instance=category,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"Category updated to '{category.name}' successfully!"
            )
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    return redirect("categories")


@login_required
def manage_budgets(request):
    current_month = timezone.localdate().replace(day=1)
    budgets = Budget.objects.filter(user=request.user).select_related("category")
    categories = Category.objects.filter(user=request.user)

    budgeted_category_ids = budgets.filter(
        month=current_month
    ).values_list("category_id", flat=True)

    categories_without_budget = categories.exclude(pk__in=budgeted_category_ids)

    budget_status = []
    for budget in budgets:
        budget_status.append({
            "budget": budget,
            "spent": budget.spent,
            "remaining": budget.remaining,
            "percentage": budget.percentage,
        })

    return render(request, "expenses/budgets.html", {
        "budget_status": budget_status,
        "categories": categories,
        "categories_without_budget": categories_without_budget,
        "current_month": current_month,
    })


@login_required
def add_budget(request):
    if request.method == "POST":
        data = request.POST.copy()
        data["month"] = timezone.localdate().replace(day=1)

        form = BudgetForm(
            data,
            user=request.user
        )

        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()

            messages.success(
                request,
                f"Budget for '{budget.category.name}' added successfully!"
            )

        else:
            for error in form.errors.values():
                messages.error(request, error)

    return redirect("manage_budgets")



@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == "POST":
        form = BudgetForm(
            request.POST,
            instance=budget,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, f"Budget for'{budget.category.name}' was edited successfully!")
            return redirect('manage_budgets')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('manage_budgets')

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    category_name = budget.category.name
    
    if request.method == "POST":
        budget.delete()
        messages.success(request, f"Budget for'{category_name}' was deleted successfully!")
    return redirect('manage_budgets')


@login_required
@require_POST
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)

    expenses_count = Expense.objects.filter(
        category=category,
        user=request.user,
    ).count()

    if expenses_count > 0:
        messages.error(
            request,
            f"Can't delete '{category.name}'! It has {expenses_count} expense(s) linked to it."
        )
        return redirect("categories")

    category_name = category.name
    category.delete()
    messages.success(request, f"Category '{category_name}' deleted successfully!")
    return redirect("categories")


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(
        Expense,
        id = expense_id,
        user=request.user
    )
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully!")

    if request.POST.get("source") == "transactions":
        return redirect("transactions")

    return redirect("home")


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user,
    )

    if request.method == "POST":
        form = ExpenseForm(
            request.POST,
            instance=expense,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Expense updated successfully!"
            )

        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    if request.POST.get("source") == "transactions":
        return redirect("transactions")

    return redirect("home")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            return render(request, "expenses/register.html", {
                "error": "This username already exists."
            })

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")
        
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        return redirect("login")
    
    return render(request, "expenses/register.html")


@login_required
def dashboard(request):
    today = timezone.localdate()

    total_expenses = (
        Expense.objects.filter(
            user=request.user,
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('price'))['total'] or 0
    )

    current_month = today.replace(day=1)

    total_budget = (
    Budget.objects.filter(
        user=request.user,
        month=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    )

    remaining_budget = total_budget - total_expenses

    total_transactions = Expense.objects.filter(
    user=request.user,
    date__year=today.year,
    date__month=today.month
        ).count()

    categories = Category.objects.filter(user=request.user)

    current_month = timezone.localdate().replace(day=1)
    monthly_budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
    ).select_related("category")

    budget_status = []
    for budget in monthly_budgets:
        budget_status.append({
            "budget": budget,
            "spent": budget.spent,
            "percentage": budget.percentage,
        })

    context = {
        'total_expenses': total_expenses,
        'total_budget': total_budget,
        'remaining_budget': remaining_budget,
        'total_transactions': total_transactions,
        "categories": categories,
        "budget_status": budget_status,
    }

    return render(request, 'expenses/dashboard.html', context)


@login_required
def categories(request):
    user_categories = Category.objects.filter(user=request.user).order_by("name")
    return render(request, "expenses/categories.html", {
        "categories": user_categories,
    })

@login_required
def transactions(request):
    expenses = (
        Expense.objects.filter(user=request.user)
        .select_related("category")
        .order_by("-date", "-id")
    )
    return render(request, "expenses/transactions.html", {
        "expenses": expenses,
        "categories": Category.objects.filter(user=request.user).order_by("name"),
    })