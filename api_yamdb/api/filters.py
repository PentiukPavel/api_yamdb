from rest_framework.filters import BaseFilterBackend


class MyFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'category' in request.query_params:
            queryset = queryset.filter(
                category__slug=request.query_params.get('category')
            )
        if 'genre' in request.query_params:
            queryset = queryset.filter(
                genre__slug=request.query_params.get('genre')
            )
        if 'year' in request.query_params:
            queryset = queryset.filter(
                year=request.query_params.get('year')
            )
        if 'name' in request.query_params:
            queryset = queryset.filter(
                name__contains=request.query_params.get('name')
            )
        return queryset
