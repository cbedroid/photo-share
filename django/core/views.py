from django.db.models import Count, Q, Sum
from django.views.generic import ListView
from gallery.models import Category, Gallery


class HomeListView(ListView):
    model = Gallery
    template_name = "core/index.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        qs = Gallery.objects.filter(public=True)

        # Preform lookup searches in all Gallery's related field
        search = self.request.GET.get("q")
        if search:
            return Gallery.objects.query_search(search, qs)

        # show only top 20 gallery with the most views
        return qs.annotate(photo_views=Sum("photos__views")).order_by("-photo_views")[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # show top 20 trending category
        context["by_search"] = self.request.GET.get("q", False)
        context["top_category"] = Category.objects.alias(c=Count("gallery")).order_by("-c")[:20]
        return context
