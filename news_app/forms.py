from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article


class CustomUserCreationForm(UserCreationForm):
    """
    Form to create a new user with a role (reader, journalist, editor).
    """

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }


class ArticleForm(forms.ModelForm):
    """
    Form to create or edit an article. Only journalists can create articles.
    """

    class Meta:
        model = Article
        fields = ("title", "content", "publisher")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "publisher": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        return title
