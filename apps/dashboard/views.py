from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        context = self.get_context_data(**kwargs)
        context = {
            "title": 'Dashboard'
        }
        return self.render_to_response(context)
