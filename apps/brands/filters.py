from admin_auto_filters.filters import AutocompleteFilter


class BrandFilter(AutocompleteFilter):
    title = 'Brand'
    field_name = 'brand'