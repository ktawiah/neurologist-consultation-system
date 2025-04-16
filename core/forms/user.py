from django import forms
from django.contrib.auth.forms import UserCreationForm
from ..models.user import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        # Add role choices
        self.fields['role'] = forms.ChoiceField(
            choices=User.Role.choices,
            required=True,
            help_text='Select your role in the system'
        )
