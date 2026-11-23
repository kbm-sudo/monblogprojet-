# blogapp/tests.py
# Quelques tests pour verifier que tout marche : python manage.py test
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Article, Commentaire


class BlogTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('user1', password='motdepasse123')
        self.u2 = User.objects.create_user('user2', password='motdepasse123')
        self.article = Article.objects.create(titre='Article A', contenu='Contenu A', auteur=self.u1)

    def test_pages_publiques(self):
        for nom in ['accueil', 'connexion', 'inscription']:
            self.assertEqual(self.client.get(reverse('blogapp:' + nom)).status_code, 200)
        self.assertEqual(self.client.get(reverse('blogapp:detail_article', args=[self.article.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('blogapp:profil_utilisateur', args=['user1'])).status_code, 200)

    def test_inscription_connecte_et_redirige(self):
        r = self.client.post(reverse('blogapp:inscription'),
                             {'username': 'nouveau', 'password1': 'Zx9!kLm2pQw', 'password2': 'Zx9!kLm2pQw'})
        self.assertRedirects(r, reverse('blogapp:accueil'))
        self.assertTrue(User.objects.filter(username='nouveau').exists())

    def test_creer_article_demande_connexion(self):
        r = self.client.get(reverse('blogapp:creer_article'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/connexion/', r.url)

    def test_creer_article(self):
        self.client.login(username='user1', password='motdepasse123')
        r = self.client.post(reverse('blogapp:creer_article'), {'titre': 'Nouveau', 'contenu': 'Texte'})
        article = Article.objects.get(titre='Nouveau')
        self.assertEqual(article.auteur, self.u1)
        self.assertRedirects(r, reverse('blogapp:detail_article', args=[article.pk]))

    def test_seul_l_auteur_modifie_et_supprime(self):
        self.client.login(username='user2', password='motdepasse123')
        self.client.post(reverse('blogapp:modifier_article', args=[self.article.pk]),
                         {'titre': 'Pirate', 'contenu': 'x'})
        self.client.post(reverse('blogapp:supprimer_article', args=[self.article.pk]))
        self.article.refresh_from_db()
        self.assertEqual(self.article.titre, 'Article A')

    def test_auteur_modifie_puis_supprime(self):
        self.client.login(username='user1', password='motdepasse123')
        self.client.post(reverse('blogapp:modifier_article', args=[self.article.pk]),
                         {'titre': 'Modifie', 'contenu': 'x'})
        self.article.refresh_from_db()
        self.assertEqual(self.article.titre, 'Modifie')
        self.client.post(reverse('blogapp:supprimer_article', args=[self.article.pk]))
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())

    def test_commentaires(self):
        url = reverse('blogapp:ajouter_commentaire', args=[self.article.pk])
        # l'auteur ne peut pas commenter son article
        self.client.login(username='user1', password='motdepasse123')
        self.client.post(url, {'contenu': 'Moi-même'})
        self.assertEqual(Commentaire.objects.count(), 0)
        # un autre utilisateur peut
        self.client.login(username='user2', password='motdepasse123')
        self.client.post(url, {'contenu': 'Bravo'})
        self.assertEqual(Commentaire.objects.count(), 1)
        r = self.client.get(reverse('blogapp:detail_article', args=[self.article.pk]))
        self.assertContains(r, 'Bravo')

    def test_pagination(self):
        for i in range(7):
            Article.objects.create(titre=f'Art {i}', contenu='x', auteur=self.u1)  # 8 articles au total
        r = self.client.get(reverse('blogapp:accueil'))
        self.assertEqual(len(r.context['articles_a_afficher']), 5)
        r = self.client.get(reverse('blogapp:accueil') + '?page=2')
        self.assertEqual(len(r.context['articles_a_afficher']), 3)
        self.assertEqual(self.client.get(reverse('blogapp:accueil') + '?page=toto').status_code, 200)
        self.assertEqual(self.client.get(reverse('blogapp:accueil') + '?page=999').status_code, 200)

    def test_deconnexion(self):
        self.client.login(username='user1', password='motdepasse123')
        r = self.client.get(reverse('blogapp:deconnexion'))
        self.assertRedirects(r, reverse('blogapp:accueil'))
