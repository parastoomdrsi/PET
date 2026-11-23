from django import forms
from .models import Budget, Category, Expense
from django.utils import timezone


class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = [
            "category",
            "amount",
            "month",
        ]

        widgets = {
            "month": forms.DateInput(
                attrs={
                    "type": "month"
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.instance.user = user

            self.fields["category"].queryset = Category.objects.filter(
                user=user
            )

        if not self.instance.pk:
            self.fields["month"].initial = (
                timezone.localdate().replace(day=1)
            )



class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "title",
            "price",
            "category",
            "date",
            "description",
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields["category"].queryset = user.categories.all()

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError(
                "Title cannot be empty."
            )

        return title

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price <= 0:
            raise forms.ValidationError(
                "Price must be greater than zero."
            )

        return price

    def clean_description(self):
        description = self.cleaned_data.get("description", "")

        if len(description) > 500:
            raise forms.ValidationError(
                "Description is too long."
            )

        return description
    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "Category name can't be empty."
            )

        if Category.objects.filter(
            user=self.user,
            name__iexact=name,
        ).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError(
                "This category already exists."
            )

        return name