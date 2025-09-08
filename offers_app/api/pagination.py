from rest_framework.pagination import PageNumberPagination

class OffersGetPagination(PageNumberPagination):
    """Custom pagination for offers with default page size of 6."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'