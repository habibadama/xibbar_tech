from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, ContactMessage, Post

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none',
                'placeholder': 'Partagez votre avis sur cet article...'
            }),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Adresse e-mail')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email


INPUT_CLASSES = (
    'w-full px-4 py-2 border border-gray-200 rounded-lg '
    'focus:ring-2 focus:ring-indigo-500 focus:outline-none'
)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags', 'cover_image', 'excerpt', 'content', 'status']
        labels = {
            'title': 'Titre',
            'category': 'Catégorie',
            'tags': 'Tags',
            'cover_image': 'Image de couverture',
            'excerpt': 'Résumé',
            'content': 'Contenu',
            'status': 'Statut',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': "Le titre de votre article",
            }),
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'tags': forms.CheckboxSelectMultiple(),
            'cover_image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': (
                    'w-full text-sm text-gray-600 '
                    'file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 '
                    'file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100'
                ),
            }),
            'excerpt': forms.Textarea(attrs={
                'rows': 3,
                'maxlength': 300,
                'class': INPUT_CLASSES,
                'placeholder': "Un court résumé (300 caractères maximum)",
            }),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
        }


CONTACT_INPUT_CLASSES = (
    'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 text-sm '
    'focus:outline-none focus:border-indigo-600 transition-colors shadow-sm'
)


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': CONTACT_INPUT_CLASSES,
                'placeholder': 'Votre nom',
            }),
            'email': forms.EmailInput(attrs={
                'class': CONTACT_INPUT_CLASSES,
                'placeholder': 'votre@email.com',
            }),
            'message': forms.Textarea(attrs={
                'class': CONTACT_INPUT_CLASSES,
                'rows': 5,
                'placeholder': 'Votre message...',
            }),
        }