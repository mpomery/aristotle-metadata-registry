from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


class MarkAllReadApiView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        self.request.user.notifications.mark_all_as_read()

        return JsonResponse({'status': 'success'})

    def handle_no_permission(self):

        return JsonResponse({'status': 'failed'})
