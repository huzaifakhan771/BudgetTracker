from drf_spectacular.utils import OpenApiParameter


class SwaggerParams:
    CONTRIBUTOR = OpenApiParameter(name="contributor", description="contributor name", type=str)
    START_YEAR_MONTH = OpenApiParameter(
        name="start_year_month", description="start year-month for range e.g. 2022-03", type=str
    )
    END_YEAR_MONTH = OpenApiParameter(
        name="end_year_month", description="end year-month for range e.g. 2022-06", type=str
    )
    CONTRIBUTION = OpenApiParameter(name="contribution", description="contribution amount", type=str)
    MONTH = OpenApiParameter(name="month", description="month at which the contribution was done", type=str)
    UUID = OpenApiParameter(name="unique_id", description="unique identifier for the contribution", type=str)
