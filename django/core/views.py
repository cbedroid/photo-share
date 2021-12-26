from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView

from .forms import ContactUsForm
from .models import FAQ, FAQTopic

User = get_user_model()


class HomeView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "PhotoShare"
        return context

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("gallery:gallery-list")
        return super().get(*args, **kwargs)


class FAQView(ListView):
    model = FAQ
    template_name = "core/faq_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faq_topics"] = FAQTopic.objects.all()
        return context


class AboutUsView(TemplateView):
    template_name = "snippets/about_us.html"


class PrivacyPolicyView(TemplateView):
    template_name = "snippets/privacy_policy.html"


class TermsConditionsView(TemplateView):
    template_name = "snippets/terms_conditions.html"


class ContactUsView(FormView):
    template_name = "core/contact_us.html"
    form_class = ContactUsForm
    success_url = "."

    def form_valid(self, form):
        if form.is_valid():
            data = form.cleaned_data
            data = dict(
                subject="Contact Us Question",
                message=f"{data['message']}\n{data['name']}\n{data['email']}",
                from_email=None,
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            try:
                send_mail(**data)
                messages.success(self.request, "Thank You, Your message was sent successfully! ")
            except BadHeaderError:
                messages.warn(
                    self.request,
                    "Hmmm... There seems to be something wrong with your message. Please try again later while we resolve this problem",
                )
        else:
            messages.warn(self.request, "Oh No..., Something went wrong. Please try sending your message again.")
        return super().form_valid(form)


def handle_403_view(request, *args, **kwargs):
    return render(request, "errors/403.html", {})


def handle_404_view(request, *args, **kwargs):
    return render(request, "errors/404.html", {})


def handle_500_view(request, *args, **kwargs):
    return render(request, "errors/500.html", {})
