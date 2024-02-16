from admin_auto_filters.filters import AutocompleteFilter
from django.utils.translation import gettext_lazy as _
from more_admin_filters import MultiSelectRelatedDropdownFilter


class MultiSelectDropdownFilter(MultiSelectRelatedDropdownFilter):
    template = 'admin/sts/filters/multiselect_dropdown_list_filter.html'


class LocationFilter(AutocompleteFilter):
    title = 'User Location'
    field_name = 'location'


class SearchLocationFilter(AutocompleteFilter):
    title = 'Search Location'
    field_name = 'search_location'


class DeviceFilter(AutocompleteFilter):
    title = 'Device'
    field_name = 'device'
    
    
