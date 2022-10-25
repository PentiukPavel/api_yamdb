from django_filters import CharFilter, FilterSet

from reviews.models import Title


class TtileFilter(FilterSet):
    """Фильтр по произведениям."""
    genre = CharFilter(field_name='genre__slug', lookup_expr='exact')
    category = CharFilter(field_name='category__slug', lookup_expr='exact')
    name = CharFilter(field_name='name', lookup_expr='contains')
    year = CharFilter(field_name='year', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'year', 'name', ]
