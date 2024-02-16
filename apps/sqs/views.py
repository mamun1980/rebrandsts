from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Q
from .models import SetListES, SiteEnableSetsES
from .forms import SetListESForm, SetListESNewForm, SiteEnableSetsESForm
from core.utils import Utils


class SetListESListView(LoginRequiredMixin, ListView):
    template_name = 'sts/setlistes_list.html'
    model = SetListES
    paginate_by = 10
    ordering = ['-updated_at']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):
        paginate_by_url = self.request.GET.get("paginate_by")
        if paginate_by_url:
            self.request.session['paginate_by'] = paginate_by_url

        paginate_by_url = self.request.session.get('paginate_by', page_size)

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=paginate_by_url, page_number=int(page_number)
        )

    def get_queryset(self):
        id_list = self.request.GET.getlist('bulk_delete_ids')
        search = self.request.GET.get('search')
        if id_list:
            brand_id = [int(ids) for ids in id_list]
            self.partner_delete(brand_id)
        queryset = SetListES.objects.order_by('-id')
        if search:
            search = search.strip()
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

    @staticmethod
    def partner_delete(id_list: list):
        obj_list = SetListES.objects.filter(id__in=id_list)
        obj_list.delete()


class SetListESListDetailView(LoginRequiredMixin, DetailView):
    template_name = 'sqs/setlistes_details.html'
    model = SetListES


class SetListESListCreateView(LoginRequiredMixin, CreateView):
    template_name = 'sqs/setlistes_create.html'
    model = SetListES
    form_class = SetListESNewForm
    success_url = '/sqs/set-list-es/'
    # fields = ['name', 'alias', 'key', 'partners']

    def form_valid(self, form):
        # latest_id = SetListES.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1
        return super().form_valid(form)


class SetListESListUpdateView(LoginRequiredMixin, UpdateView):
    model = SetListES
    form_class = SetListESNewForm
    success_url = '/sqs/set-list-es/'


class SetListESListDeleteView(LoginRequiredMixin, DeleteView):
    model = SetListES
    success_url = "/sqs/set-list-es/"


class SiteEnableSetsESListView(LoginRequiredMixin, ListView):
    template_name = 'sts/siteenablesetses_list.html'
    model = SiteEnableSetsES
    paginate_by = 10
    ordering = ['-updated_at']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):
        paginate_by_url = self.request.GET.get("paginate_by")
        if paginate_by_url:
            self.request.session['paginate_by'] = paginate_by_url

        paginate_by_url = self.request.session.get('paginate_by', page_size)

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=paginate_by_url, page_number=int(page_number)
        )

    def get_queryset(self):
        id_list = self.request.GET.getlist('bulk_delete_ids')
        search = self.request.GET.get('search')
        if id_list:
            brand_id = [int(ids) for ids in id_list]
            self.partner_delete(brand_id)
        queryset = SiteEnableSetsES.objects.order_by('-id')
        if search:
            search = search.strip()
            queryset = queryset.filter(Q(set_list__name__icontains=search))
        return queryset

    @staticmethod
    def partner_delete(id_list: list):
        obj_list = SiteEnableSetsES.objects.filter(id__in=id_list)
        obj_list.delete()


class SiteEnableSetsESCreateView(LoginRequiredMixin, CreateView):
    template_name = 'sqs/siteenablesetses_create.html'
    model = SiteEnableSetsES
    form_class = SiteEnableSetsESForm
    success_url ="/sqs/site-enable-set-es/"
    # fields = ['name', 'alias', 'key', 'partners']

    def form_valid(self, form):
        # latest_id = SetListES.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1
        return super().form_valid(form)
    

class SiteEnableSetsESDetailView(LoginRequiredMixin, DetailView):
    template_name = 'sqs/siteenablesetses_details.html'
    model = SiteEnableSetsES


class SiteEnableSetsESUpdateView(LoginRequiredMixin, UpdateView):
    model = SiteEnableSetsES
    form_class = SiteEnableSetsESForm
    success_url = '/sqs/site-enable-set-es/'


class SiteEnableSetsESDeleteView(LoginRequiredMixin, DeleteView):
    model = SiteEnableSetsES
    success_url = "/sqs/site-enable-set-es/"

