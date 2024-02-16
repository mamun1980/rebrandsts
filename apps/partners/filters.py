from admin_auto_filters.filters import AutocompleteFilter


class PartnerFilter(AutocompleteFilter):
    title = 'Filter By Partner'
    field_name = 'partner'