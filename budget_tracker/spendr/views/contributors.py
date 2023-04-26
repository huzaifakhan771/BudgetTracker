from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from budget_tracker.spendr.models import Contributors


class ListCreateContributor(APIView):
    """
    View to list, create, or delete contributors.
    """

    def get(self, request):
        """
        Return a list of all contributors.
        """
        contributors = Contributors.objects.all().values_list("name", flat=True).order_by("name")
        contributors = [contributor.capitalize() for contributor in contributors]

        return Response({"contributors": contributors}, status=status.HTTP_200_OK)

    def post(self, request):
        query_params = request.query_params

        contributor = query_params.get("contributor")

        if contributor:
            _, created = Contributors.objects.get_or_create(name=contributor.lower())
            response = f"Contributor {contributor} has been created"
            status_ = status.HTTP_201_CREATED
        else:
            response = "Please provide a contributor"
            status_ = status.HTTP_400_BAD_REQUEST

        return Response({"message": response}, status=status_)

    def delete(self, request):
        query_params = request.query_params

        contributor = query_params.get("contributor")

        if contributor:
            try:
                Contributors.objects.get(name=contributor.lower()).delete()
                response = f"Contributor {contributor} has been deleted"
                status_ = status.HTTP_200_OK
            except ObjectDoesNotExist:
                response = f"Contributor {contributor} does not exist"
                status_ = status.HTTP_404_NOT_FOUND
        else:
            response = "Please provide a contributor"
            status_ = status.HTTP_400_BAD_REQUEST

        return Response({"message": response}, status=status_)
