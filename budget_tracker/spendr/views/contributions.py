from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import CharField, Func, Sum, Value
from django.db.models.functions import Cast, Concat, ExtractMonth, ExtractYear, LPad
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from budget_tracker.spendr.models import Contributions, Contributors
from budget_tracker.spendr.swagger_constants import SwaggerParams
from budget_tracker.spendr.utils import (
    aggregate_contributions_qs,
    get_contribution_initial_query,
    is_invalid_month,
    is_invalid_year_month,
)


class ListCreateContribution(APIView):
    """
    View to list, create, or delete contributions.
    """

    @extend_schema(
        tags=["Contributions"],
        parameters=[
            SwaggerParams.CONTRIBUTOR,
            SwaggerParams.START_YEAR_MONTH,
            SwaggerParams.END_YEAR_MONTH,
        ],
    )
    def get(self, request):
        """
        Return a list of all contributions.
        """
        query_params = request.query_params

        contributor = query_params.get("contributor")
        start_year_month = query_params.get("start_year_month")
        end_year_month = query_params.get("end_year_month")

        response_dict = {}

        if start_year_month:
            response = is_invalid_year_month(start_year_month)
            if response:
                return response
        if end_year_month:
            response = is_invalid_year_month(end_year_month)
            if response:
                return response

        initial_query = get_contribution_initial_query(contributor, start_year_month, end_year_month)

        annotated_qs = initial_query.annotate(
            year_month=Concat(
                Cast(ExtractYear("contribution_date"), CharField()),
                Value("-"),
                LPad(Cast(ExtractMonth("contribution_date"), CharField()), 2, Value("0")),
            ),
            contributor_name=Capitalize("contributor__name"),
        ).values("year_month", "contributor_name", "contribution_amount", "unique_id")

        response_dict["contributions"] = annotated_qs

        total_contribution = annotated_qs.aggregate(total=Sum("contribution_amount"))["total"]
        response_dict["total_contributions"] = total_contribution

        contribution_per_contributor = aggregate_contributions_qs(annotated_qs, total_contribution)
        response_dict["contribution_per_contributor"] = contribution_per_contributor

        return Response({"response": response_dict}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Contributions"],
        parameters=[
            SwaggerParams.CONTRIBUTOR,
            SwaggerParams.MONTH,
            SwaggerParams.CONTRIBUTION,
        ],
    )
    def post(self, request):
        """
        Add a contribution with the contributor name.
        """
        query_params = request.query_params

        contributor = query_params.get("contributor")
        month = query_params.get("month")
        contribution = query_params.get("contribution")

        if all((contributor, month, contribution)):
            response = is_invalid_month(month)
            if response:
                return response

            contributor_obj = Contributors.objects.filter(name=contributor.lower())
            contributor_obj = contributor_obj.first()

            if contributor_obj:
                contribution_obj = Contributions(contributor=contributor_obj, contribution_amount=contribution)
                contribution_obj.save(month=month)

                response = f"Contribution for {contributor} has been saved"
                status_ = status.HTTP_201_CREATED
            else:
                response = f"Contributor {contributor} does not exist"
                status_ = status.HTTP_400_BAD_REQUEST
        else:
            return Response(
                {"message": "Please provide all query_parameters: contributor, month, contribution"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": response}, status=status_)

    @extend_schema(
        tags=["Contributions"],
        parameters=[
            SwaggerParams.UUID,
        ],
    )
    def delete(self, request):
        """
        Delete a contribution by using its unique identifier
        """
        query_params = request.query_params
        unique_id = query_params.get("unique_id")
        if unique_id:
            try:
                Contributions.objects.get(unique_id=unique_id).delete()
                response = f"Contribution {unique_id} has been deleted"
                status_ = status.HTTP_200_OK
            except ObjectDoesNotExist:
                response = f"Contribution {unique_id} does not exist"
                status_ = status.HTTP_400_BAD_REQUEST
            except ValidationError:
                response = f"Invalid unique_id: {unique_id}"
                status_ = status.HTTP_400_BAD_REQUEST
        else:
            response = "Please provide a unique_id"
            status_ = status.HTTP_400_BAD_REQUEST

        return Response({"message": response}, status=status_)


class Capitalize(Func):
    function = "INITCAP"
    template = "%(function)s(%(expressions)s)"
