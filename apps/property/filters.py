from admin_auto_filters.filters import AutocompleteFilter


class PropertyGroupFilter(AutocompleteFilter):
    title = 'Accommodation Type'
    field_name = 'property_group'
