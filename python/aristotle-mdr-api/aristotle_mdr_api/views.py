from django.views.generic import TemplateView

class APIRootView(TemplateView):
    template_name = "aristotle_mdr_api/base.html"
