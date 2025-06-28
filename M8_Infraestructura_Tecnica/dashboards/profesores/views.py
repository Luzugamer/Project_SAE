from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class DashboardProfesorView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboards/profesor.html'

    def test_func(self):
        return self.request.user.es_profesor  