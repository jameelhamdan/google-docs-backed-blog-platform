from django.views import generic


class ActionView(generic.detail.SingleObjectMixin, generic.RedirectView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.action()
        return super().get(request, *args, **kwargs)

    def action(self):
        """
        Overridable method to do a specific action
        :return:
        """
        pass
