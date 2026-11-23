from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_user_category",
            ),
        ]

    def __str__(self):
        return self.name


class Expense(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.localdate)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    class Meta:
        ordering = ("-date", "-created_at")

    def __str__(self):
        return self.title


class Budget(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(help_text="First day of the month")

    class Meta:
        ordering = ("-month",)
        constraints = [
            models.UniqueConstraint(
                fields=["category", "user", "month"],
                name="unique_budget",
            ),
        ]

    def __str__(self):
        return f"{self.category} ({self.month:%B %Y})"

    def clean(self):
        super().clean()

        if self.amount is not None and self.amount <= 0:
            raise ValidationError({
                "amount": "Budget must be greater than 0."
            })

        if self.month and self.month.day != 1:
            raise ValidationError({
                "month": "Month must be the first day of the month."
            })

        if self.category_id and self.user_id:
            if self.category.user_id != self.user_id:
                raise ValidationError({
                    "category": "The selected category does not belong to this user."
                })
            

    @property
    def spent(self) -> Decimal:
        total = (
            Expense.objects.filter(
                category=self.category,
                user=self.user,
                date__year=self.month.year,
                date__month=self.month.month,
            )
            .aggregate(total=Sum("price"))
            .get("total")
        )

        return total or Decimal("0.00")

    @property
    def remaining(self) -> Decimal:
        return self.amount - self.spent

    @property
    def percentage(self) -> int:
        if self.amount == 0:
            return 0

        return round((self.spent / self.amount) * 100)