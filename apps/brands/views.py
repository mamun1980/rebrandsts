from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Q
from .models import Brand
from .forms import BrandForm
from core.utils import Utils


class BrandsListView(LoginRequiredMixin, ListView):
    template_name = 'brands/list.html'
    model = Brand
    paginate_by = 10
    ordering = ['-updated_at']
    utils = Utils()

    def get_queryset(self):
        id_list = self.request.GET.getlist('bulk_delete_ids')
        search = self.request.GET.get('search')
        if id_list:
            brand_id = [int(ids) for ids in id_list]
            self.brands_delete(brand_id)
        queryset = Brand.objects.order_by('-id')
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
    def brands_delete(id_list: list):
        obj_list = Brand.objects.filter(id__in=id_list)
        obj_list.delete()


class BrandsDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'brands/details.html'
    model = Brand


class BrandsCreateView(LoginRequiredMixin, CreateView):
    template_name = 'brands/add-brands.html'
    model = Brand
    form_class = BrandForm
    # fields = ['name', 'alias', 'key', 'partners']

    def form_valid(self, form):
        # latest_id = Brand.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1 if latest_id else 1
        return super().form_valid(form)


class BrandsUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'brands/update-brand.html'
    model = Brand
    form_class = BrandForm
    success_url = '/brands/'


class BrandSDeleteView(LoginRequiredMixin, DeleteView):
    model = Brand
    success_url = "/brands/"
