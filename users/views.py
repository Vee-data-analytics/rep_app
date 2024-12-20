from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'admin/user_form.html'
    success_url = reverse_lazy('reptrack_trace:user-list')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.exclude(username='admin')  # Exclude admin from list

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'admin/user_form.html'
    success_url = reverse_lazy('reptrack_trace:user-list')

    def get_queryset(self):
        # Prevent editing admin user through this view
        return User.objects.exclude(username='admin')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'admin/user_confirm_delete.html'
    success_url = reverse_lazy('reptrack_trace:user-list')

    def get_queryset(self):
        # Prevent deleting admin user
        return User.objects.exclude(username='admin')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User delete')


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'admin/user_form.html'
    success_url = reverse_lazy('reptrack_trace:user-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add any additional processing here if needed
        return response

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'admin/user_form.html'
    success_url = reverse_lazy('reptrack_trace:user-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add any additional processing here if needed
        return response


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone_number')
