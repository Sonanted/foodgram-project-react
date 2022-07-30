from rest_framework.pagination import PageNumberPagination


class FoodPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'limit'
