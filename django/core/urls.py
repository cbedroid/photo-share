from django.urls import re_path

from . import views

app_name = "core"
urlpatterns = [
    re_path(r"^terms-conditions/$", views.TermsConditionView.as_view(), name="terms-conditions"),
    re_path(r"^privacy-policy/$", views.PrivacyPolicyView.as_view(), name="privacy-policy"),
    re_path(r"^contact-us/$", views.ContactUsView.as_view(), name="contact-us"),
    re_path(r"^about-us/$", views.AboutUsView.as_view(), name="about-us"),
    re_path(r"^faqs/$", views.FAQListView.as_view(), name="faqs"),
    re_path("", views.HomeView.as_view(), name="index"),
]
