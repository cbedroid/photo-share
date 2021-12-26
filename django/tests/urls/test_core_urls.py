from core.views import *
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestUrls(SimpleTestCase):
    def test_index_url_is_resolved(self):
        url = reverse("core:index")
        self.assertEqual(resolve(url).func.view_class, HomeView)

    def test_contact_us_url_is_resolved(self):
        url = reverse("core:contact-us")
        self.assertEqual(resolve(url).func.view_class, ContactUsView)

    def test_FAQ_us_url_is_resolved(self):
        url = reverse("core:faqs")
        self.assertEqual(resolve(url).func.view_class, FAQView)

    def test_Privacy_Policy_url_is_resolved(self):
        url = reverse("core:privacy-policy")
        self.assertEqual(resolve(url).func.view_class, PrivacyPolicyView)

    def test_Terms_and_Conditions_url_is_resolved(self):
        url = reverse("core:terms-conditions")
        self.assertEqual(resolve(url).func.view_class, TermsConditionsView)
