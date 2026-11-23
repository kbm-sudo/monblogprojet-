# blogapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Article, Commentaire
from .forms import ArticleForm, CommentaireForm


# ---------- Accueil (avec pagination) ----------

def accueil_view(request):
    tous_les_articles = Article.objects.all().order_by('-date_creation')

    paginator = Paginator(tous_les_articles, 5)  # 5 articles par page
    page_numero = request.GET.get('page')

    try:
        articles_pages = paginator.page(page_numero)
    except PageNotAnInteger:
        # si 'page' n'est pas un entier, on affiche la premiere page
        articles_pages = paginator.page(1)
    except EmptyPage:
        # si la page n'existe pas, on affiche la derniere
        articles_pages = paginator.page(paginator.num_pages)

    context = {
        'articles_a_afficher': articles_pages,
    }
    return render(request, 'blogapp/accueil.html', context)


# ---------- Authentification ----------

def inscription_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # on connecte directement l'utilisateur
            return redirect('blogapp:accueil')
    else:
        form = UserCreationForm()
    return render(request, 'blogapp/inscription.html', {'form': form})


def connexion_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # si l'utilisateur vient d'une page protegee, on le renvoie dessus
            suivant = request.GET.get('next')
            if suivant and suivant.startswith('/'):
                return redirect(suivant)
            return redirect('blogapp:accueil')
    else:
        form = AuthenticationForm()
    return render(request, 'blogapp/connexion.html', {'form': form})


def deconnexion_view(request):
    # version simple : deconnexion avec un lien (GET), comme dans le cours
    logout(request)
    return redirect('blogapp:accueil')


# ---------- Articles ----------

@login_required
def creer_article_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            nouvel_article = form.save(commit=False)
            nouvel_article.auteur = request.user
            nouvel_article.save()
            return redirect('blogapp:detail_article', pk=nouvel_article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blogapp/creer_modifier_article.html', {'form': form, 'action': 'Créer'})


def detail_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    commentaire_form = CommentaireForm()
    context = {
        'article': article,
        'commentaire_form': commentaire_form,
    }
    return render(request, 'blogapp/detail_article.html', context)


@login_required
def modifier_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # seul l'auteur peut modifier
    if article.auteur != request.user:
        return redirect('blogapp:detail_article', pk=article.pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('blogapp:detail_article', pk=article.pk)
    else:
        form = ArticleForm(instance=article)

    context = {
        'form': form,
        'action': 'Modifier',
        'article': article,
    }
    return render(request, 'blogapp/creer_modifier_article.html', context)


@login_required
def supprimer_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if article.auteur != request.user:
        return redirect('blogapp:detail_article', pk=article.pk)

    if request.method == 'POST':
        article.delete()
        return redirect('blogapp:accueil')

    return render(request, 'blogapp/confirmer_suppression_article.html', {'article': article})


# ---------- Commentaires ----------

@login_required
def ajouter_commentaire_view(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    # l'auteur de l'article ne peut pas commenter son propre article
    if article.auteur == request.user:
        return redirect('blogapp:detail_article', pk=article.pk)

    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user
            commentaire.save()
    return redirect('blogapp:detail_article', pk=article.pk)


# ---------- Profil ----------

def profil_utilisateur_view(request, username):
    utilisateur_profil = get_object_or_404(User, username=username)
    articles_utilisateur = Article.objects.filter(auteur=utilisateur_profil).order_by('-date_creation')
    context = {
        'utilisateur_profil': utilisateur_profil,
        'articles_utilisateur': articles_utilisateur,
    }
    return render(request, 'blogapp/profil_utilisateur.html', context)
