from django.urls import path

from budget_tracker.spendr.views import budget_status, contributions, contributors, expenses

urlpatterns = [
    path(route="contributors", view=contributors.ListCreateContributor.as_view(), name="contributors_endpoint"),
    path(route="contributions", view=contributions.ListCreateContribution.as_view(), name="contributions_endpoint"),
    path(route="expenses", view=expenses.ListCreateExpenses.as_view(), name="expenses_endpoint"),
    path(route="budget_status", view=budget_status.ListCreateBudgetStatus.as_view(), name="status_endpoint"),
]
