# blogapp/forms.py
from django import forms
from .models import Article, Commentaire


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu']  # l'auteur et les dates sont geres dans la vue / le modele


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Laissez votre commentaire ici...'}),
        }
