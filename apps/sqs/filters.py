from admin_auto_filters.filters import AutocompleteFilter


class LocBrandFilter(AutocompleteFilter):
    title = 'Filter By Brand'
    field_name = 'loc'


class LocLocationFilter(AutocompleteFilter):
    title = 'Filter By Location'
    field_name = 'location'