from rest_framework.pagination import PageNumberPagination


class CustomLimitPagination(PageNumberPagination):
    """Пагинатор для для отображения элементов на странице."""
    page_size_query_param = "limit"
    page_size = 6