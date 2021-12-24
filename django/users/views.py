from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.edit import DeleteView

from .forms import AccountDeleteForm, UserUpdateForm

User = get_user_model()


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    login_url = reverse_lazy("account_login")
    template = "user/user_form.html"

    def test_func(self):
        return self.request.user == self.get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        self.object = self.get_object()
        if self.request.method == "GET":
            context["form"] = self.form_class(instance=obj)
        else:
            context["form"] = self.form_class(instance=obj, data=self.request.POST)
        return context

    def get_success_url(self):
        return self.get_object().get_update_url()


class UserAccountDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    form_class = AccountDeleteForm
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("core:index")

    def test_func(self):
        return self.request.user == self.get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        self.object = self.get_object()
        if self.request.method == "GET":
            context["form"] = self.form_class(instance=obj)
        else:
            context["form"] = self.form_class(instance=obj, data=self.request.POST)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        if form.has_changed and form.is_valid():
            # send an email to user
            # delete user account
            form.save(commit=True)
            return super().form_valid(form)
        else:
            context["form"] = form
            return super().form_invalid(form)
