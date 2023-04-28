from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from budget_tracker.spendr.models import Expenses
from budget_tracker.spendr.utils import aggregate_expenses_qs, get_expenses_initial_query, is_invalid_date


class ListCreateExpenses(APIView):
    """
    View to list, create, or delete contributors.
    """

    def get(self, request):
        """
        Return a list of all expenses.
        """
        query_params = request.query_params

        item_name = query_params.get("item_name")
        start_date = query_params.get("start_date")
        end_date = query_params.get("end_date")
        added_by = query_params.get("added_by")

        response_dict = {}

        if start_date:
            response = is_invalid_date(start_date)
            if response:
                return response

        if end_date:
            response = is_invalid_date(end_date)
            if response:
                return response

        initial_query = get_expenses_initial_query(item_name, start_date, end_date, added_by)

        result_qs = initial_query.values(
            "item_name", "item_price", "added_by", "item_quantity", "date_added", "unique_id", "total_price"
        ).order_by("-date_added", "-total_price")

        response_dict["expenses"] = result_qs

        total_expenses = result_qs.aggregate(total_expenses=Sum("total_price"))["total_expenses"]
        response_dict["total_expenses"] = total_expenses

        expense_per_item = aggregate_expenses_qs(result_qs, total_expenses)
        response_dict["expense_per_item"] = expense_per_item

        return Response({"response": response_dict})

    def post(self, request):
        query_params = request.query_params

        item_name = query_params.get("item_name")
        item_price = query_params.get("item_price")
        date_added = query_params.get("date")
        item_quantity = query_params.get("item_quantity")
        added_by = request.user.name

        if not all((item_name, item_price)):
            return Response(
                {"message": "Both item_name and item_price are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not item_price.isdigit() or int(item_price) < 0:
            return Response({"message": "Provide a valid item price value"}, status=status.HTTP_400_BAD_REQUEST)

        if date_added:
            response = is_invalid_date(date_added)
            if response:
                return response

        if item_quantity:
            if not item_quantity.isdigit() or int(item_quantity) < 1:
                return Response({"message": "Provide a valid item quantity value"}, status=status.HTTP_400_BAD_REQUEST)

        expenses = Expenses(added_by=added_by, item_name=item_name.lower(), item_price=item_price)

        if date_added:
            expenses.date_added = date_added
        if item_quantity:
            expenses.item_quantity = item_quantity

        expenses.save()

        return Response({"message": f"Expense has been saved for {item_name}"}, status=status.HTTP_200_OK)

    def delete(self, request):
        query_params = request.query_params
        unique_id = query_params.get("unique_id")
        if unique_id:
            try:
                Expenses.objects.get(unique_id=unique_id).delete()
                response = f"Expense {unique_id} has been deleted"
                status_ = status.HTTP_200_OK
            except ObjectDoesNotExist:
                response = f"Expense {unique_id} does not exist"
                status_ = status.HTTP_400_BAD_REQUEST
            except ValidationError:
                response = f"Invalid unique_id: {unique_id}"
                status_ = status.HTTP_400_BAD_REQUEST
        else:
            response = "Please provide a unique_id"
            status_ = status.HTTP_400_BAD_REQUEST

        return Response({"message": response}, status=status_)
