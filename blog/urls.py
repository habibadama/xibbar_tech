from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Pages générales
    path('', views.home, name='home'),
    path('recherche/', views.search, name='search'),
    path('a_propos/', views.about, name='about'),

    # Authentification
    path('inscription/', views.register_view, name='register'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='blog/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Catégories et tags
    path('categorie/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tags/', views.tags_list, name='tags_list'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),

    # Articles : CRUD (utilisateurs connectés)
    path('mes-articles/', views.my_posts, name='my_posts'),
    path('nouvel-article/', views.post_create, name='post_create'),
    path('article/<slug:slug>/', views.post_detail, name='post_detail'),
    path('article/<slug:slug>/modifier/', views.post_update, name='post_update'),
    path('article/<slug:slug>/supprimer/', views.post_delete, name='post_delete'),
    path('contact/', views.contact_view, name='contact'),
]