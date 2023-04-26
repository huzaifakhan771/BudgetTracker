import datetime
import re

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from budget_tracker.spendr.models import Contributions, Expenses


def is_invalid_month(month):
    current_month = datetime.date.today().month
    error_response_message = "Please enter correct month"
    status_ = status.HTTP_400_BAD_REQUEST
    try:
        month = int(month)
        if month < 1 or month > current_month:
            return Response({"message": error_response_message}, status=status_)
    except ValueError:
        return Response({"message": error_response_message}, status=status_)


def is_invalid_year(year):
    pattern = re.compile(r"^\d{4}$")
    error_response_message = "Please enter correct year"
    if pattern.match(year):
        year_int = int(year)
        current_year = datetime.datetime.now().year
        if 2000 <= year_int <= current_year:
            return False

    return Response({"message": error_response_message}, status=status.HTTP_400_BAD_REQUEST)


def is_invalid_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return False
    except ValueError:
        return Response({"message": "Provide a valid date format: YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)


def is_invalid_year_month(year_month):
    pattern = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
    error_response_message = "Please enter correct year month in format YYYY-MM"
    if pattern.match(year_month):
        year, month = map(int, year_month.split("-"))
        current_year, current_month = datetime.datetime.now().year, datetime.datetime.now().month
        if year > current_year or (year == current_year and month > current_month):
            error_response_message = "year or month cannot be greater than current date"
        else:
            return False

    return Response({"message": error_response_message}, status=status.HTTP_400_BAD_REQUEST)


def get_contribution_initial_query(contributor, start_year_month, end_year_month):
    query = Q()

    if contributor:
        query = query & Q(contributor__name=contributor)

    if start_year_month:
        year, month = start_year_month.split("-")
        query = query & Q(contribution_date__year__gte=year, contribution_date__month__gte=month)

    if end_year_month:
        year, month = end_year_month.split("-")
        query = query & Q(contribution_date__year__lte=year, contribution_date__month__lte=month)

    return Contributions.objects.filter(query)


def get_expenses_initial_query(item_name, start_date, end_date, added_by):
    query = Q()

    if item_name:
        query = query & Q(item_name=item_name.lower())

    if start_date:
        query = query & Q(date_added__gte=start_date)

    if end_date:
        query = query & Q(date_added__lte=end_date)

    if added_by:
        query = query & Q(added_by=added_by)

    return Expenses.objects.filter(query)


def aggregate_contributions_qs(queryset, total_contribution):
    result = {}
    for record in queryset:
        contributor = record.get("contributor_name")
        contribution = record.get("contribution_amount")

        result.setdefault(contributor, {"amount": 0})

        result[contributor]["amount"] += contribution

    for key, value in result.items():
        result[key]["percentage"] = round((value["amount"] * 100) / total_contribution, 2)

    return result


def aggregate_expenses_qs(queryset, total_expenses):
    result = {}
    for record in queryset:
        item = record.get("item_name")
        item_total_price = record.get("total_price")

        result.setdefault(item, {"grand_total": 0})

        result[item]["grand_total"] += item_total_price

    for key, value in result.items():
        result[key]["percentage"] = round((value["grand_total"] * 100) / total_expenses, 2)

    return result
