import re

from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView as Login
from django.db import transaction
from django.http import HttpResponseRedirect

from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView

from users.models import InviteCode, Token, EmailPatternWhitelist, ContentUpdateRequest


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LoginView(Login):
    form_class = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('graph')
    template_name = 'people/login.html'


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class ContentUpdateRequestForm(forms.ModelForm):
    class Meta:
        model = ContentUpdateRequest
        fields = ('content',)


class ContentUpdateRequestView(FormView):
    form_class = ContentUpdateRequestForm
    template_name = 'people/content_update.html'
    success_url = reverse_lazy('content_update_submit')

    @transaction.atomic
    def form_valid(self, form):
        update_request = form.save(commit=False)
        update_request.submitted_by = self.request.user
        update_request.save()

        messages.success(self.request, 'Your content has been submitted for review')

        return super().form_valid(form)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    password_confirm = forms.CharField(max_length=128, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.has_invite = kwargs.pop('has_invite', False)
        super().__init__(*args, **kwargs)
        if self.has_invite:
            self.fields.pop('email')
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        if not self.has_invite and self.cleaned_data.get('email'):
            email = self.cleaned_data.get('email')
            patterns = EmailPatternWhitelist.objects.all()
            if not any([re.compile(whitelist.pattern).match(email) for whitelist in patterns]):
                self.add_error('email', 'The email pattern is invalid')

            if User.objects.filter(email=email).exists():
                self.add_error('email', 'User with this email already exists')

        if self.cleaned_data.get('username') and User.objects.filter(username=self.cleaned_data['username']).exists():
            self.add_error('username', 'User with this username already exists')

        if self.cleaned_data.get('password') and len(self.cleaned_data.get('password', '')) < 8:
            self.add_error('password', 'Password must be at least 8 characters long')
            return self.cleaned_data

        if self.cleaned_data.get('password_confirm') and self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', 'Passwords don\'t match')

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name',)


class RegistrationView(FormView):
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'people/registration.html'

    def dispatch(self, request, *args, **kwargs):
        self.invite_code = None
        if 'code' in request.GET:
            try:
                self.invite_code = InviteCode.objects.get(code=request.GET['code'], user__isnull=True)
            except InviteCode.DoesNotExist:
                pass

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['has_invite'] = self.invite_code is not None
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['invite_code'] = self.invite_code
        return data

    @transaction.atomic
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        if self.invite_code:
            self.invite_code.user = user
            self.invite_code.save()
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('graph'))

        else:
            user.is_active = False
            user.save()

            token = Token.create_for_user(user)
            token.save()

            #user.email_user(
            #    'Spmndag Graph - registration confirmation',
            #    get_template('people/activation_email.html').render({'token': token.token})
            #)
            messages.success(self.request, 'Activation link has been sent to your email')
        return super().form_valid(form)


class AccountActivationView(View):
    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(token=kwargs['token'], valid=True, type=Token.Types.ACCOUNT_ACTIVATION)
        except Token.DoesNotExist:
            return HttpResponseRedirect(reverse('registration'))

        token.user.is_active = True
        token.user.save()
        login(self.request, token.user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponseRedirect(reverse('graph'))
