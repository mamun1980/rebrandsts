from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Q
from .models import Partner, Provider
from .forms import PartnerForm, ProviderForm
from core.utils import Utils


class PartnerListView(LoginRequiredMixin, ListView):
    template_name = 'partners/list.html'
    model = Partner
    paginate_by = 10
    ordering = ['-created_at']
    utils = Utils()

    def get_queryset(self):
        id_list = self.request.GET.getlist('bulk_delete_ids')
        search = self.request.GET.get('partner_search')
        if id_list:
            brand_id = [int(ids) for ids in id_list]
            self.partner_delete(brand_id)
        queryset = Partner.objects.order_by('-id')
        if search:
            search = search.strip()
            queryset = queryset.filter(Q(name__icontains=search) | Q(key__icontains=search))
        return queryset

    def paginate_queryset(self, queryset, page_size):
        paginate_by_url = self.request.GET.get("paginate_by")
        if paginate_by_url:
            self.request.session['paginate_by'] = paginate_by_url

        paginate_by_url = self.request.session.get('paginate_by', page_size)

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=paginate_by_url, page_number=int(page_number)
        )

    @staticmethod
    def partner_delete(id_list: list):
        obj_list = Partner.objects.filter(id__in=id_list)
        obj_list.delete()


class PartnerDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'partners/details.html'
    model = Partner


class PartnerCreateView(LoginRequiredMixin, CreateView):
    template_name = 'partners/add-partner.html'
    model = Partner
    fields = ['name', 'key', 'domain_name', 'feed']

    def form_valid(self, form):
        # latest_id = Partner.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1 if latest_id else 1
        return super().form_valid(form)


class PartnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Partner
    form_class = PartnerForm
    success_url = '/partners/'


class PartnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Partner
    success_url = "/partners/"


class ProviderListView(LoginRequiredMixin, ListView):
    template_name = 'provider/list.html'
    model = Provider
    paginate_by = 10
    ordering = ['-created_at']
    utils = Utils()

    def get_queryset(self):
        id_list = self.request.GET.getlist('bulk_delete_ids')
        search = self.request.GET.get('search')
        if id_list:
            brand_id = [int(ids) for ids in id_list]
            self.partner_delete(brand_id)
        queryset = Provider.objects.order_by('-id')
        if search:
            search = search.strip()
            queryset = queryset.filter(Q(name__icontains=search) | Q(provider_id__icontains=search))
        return queryset

    def paginate_queryset(self, queryset, page_size):
        paginate_by_url = self.request.GET.get("paginate_by")
        if paginate_by_url:
            self.request.session['paginate_by'] = paginate_by_url

        paginate_by_url = self.request.session.get('paginate_by', page_size)

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=paginate_by_url, page_number=int(page_number)
        )

    @staticmethod
    def partner_delete(id_list: list):
        obj_list = Provider.objects.filter(id__in=id_list)
        obj_list.delete()


class ProviderDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'provider/details.html'
    model = Provider


class ProviderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'provider/add.html'
    model = Provider
    fields = ['name', 'provider_id']
    success_url = '/partners/provider/'


class ProviderUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'provider/provider_form.html'
    model = Provider
    form_class = ProviderForm
    success_url = '/partners/provider/'


class ProviderDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'provider/provider_confirm_delete.html'
    model = Provider
    success_url = '/partners/provider/'
