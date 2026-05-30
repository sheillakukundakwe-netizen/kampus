from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Item, ClaimRequest, Profile


class CampusAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CampusRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label='Campus email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@makerere.ac.ug'}),
    )
    campus_role = forms.ChoiceField(
        choices=Profile.Role.choices,
        label='Campus role',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = User
        fields = ['email', 'campus_role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        domain = email.split('@')[-1].lower()
        if domain not in settings.ALLOWED_EMAIL_DOMAINS:
            raise forms.ValidationError(
                'Please register with an approved campus email address.'
            )
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.campus_role = self.cleaned_data['campus_role']
            user.profile.verified = True
            user.profile.save()
        return user


class ItemReportForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'location', 'contact_info']
        labels = {
            'title': 'Item name',
            'description': 'Description',
            'location': 'Last seen location',
            'contact_info': 'Contact info',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. blue backpack or laptop'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the item clearly'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. library, lecture hall, cafeteria'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email or phone number'}),
        }
        help_texts = {
            'contact_info': 'This will help the finder contact you.',
        }


class ClaimRequestForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        fields = ['message']
        labels = {'message': 'Claim message'}
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Add details that help the reporter verify you and coordinate pickup.',
                }
            )
        }
