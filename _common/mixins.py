class PageTitleMixin:
    title = None
    title_context_name = 'page_title'
    title_object = False
    title_object_attribute = 'title'
    title_template = '%s'

    def get_page_title(self):
        if not self.title_object:
            return self.title_template % self.title
        else:
            if hasattr(self, 'object'):
                obj = self.object
            else:
                obj = self.get_object()
            return self.title_template % getattr(obj, self.title_object_attribute , None)

    def get_context_data(self, *args, **kwargs):
        context = super(PageTitleMixin, self).get_context_data(*args, **kwargs)
        context[self.title_context_name] = self.get_page_title()
        return context


class PageMixin(PageTitleMixin):
    pass
