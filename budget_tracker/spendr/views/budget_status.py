from datetime import datetime

from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from budget_tracker.spendr.models import Contributions, Expenses
from budget_tracker.spendr.utils import is_invalid_year_month


class ListCreateBudgetStatus(APIView):
    """
    View to list budget status
    """

    def get(self, request):
        """
        Return a list of budget status.
        """
        query_params = request.query_params

        default_year_month = datetime.today().strftime("%Y-%m")
        year_month = query_params.get("year_month", default_year_month)

        response_dict = {"year_month": year_month}

        year_month_validation_response = is_invalid_year_month(year_month)
        if year_month_validation_response:
            return year_month_validation_response

        year, month = year_month.split("-")

        total_expenses = Expenses.objects.filter(date_added__year=year, date_added__month=month).aggregate(
            total_expenses=Sum("item_price")
        )["total_expenses"]

        response_dict["total_expenses"] = total_expenses

        total_contribution = Contributions.objects.filter(
            contribution_date__year=year, contribution_date__month=month
        ).aggregate(total_contribution=Sum("contribution_amount"))["total_contribution"]

        response_dict["total_contribution"] = total_contribution

        if total_contribution and total_expenses:
            response_dict["remaining_budget"] = total_contribution - total_expenses
        else:
            response_dict["remaining_budget"] = None

        return Response({"response": response_dict})
