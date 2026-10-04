from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils import timezone
from django.utils.text import slugify

from blog.forms import CommentForm, ContactForm, PostForm, RegisterForm
from blog.models import Post, Category, Tag
from django.core.mail import send_mail

POSTS_PER_PAGE = 5


def register_view(request):
    # Un utilisateur déjà connecté n'a rien à faire sur la page d'inscription
    if request.user.is_authenticated:
        return redirect('blog:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()      # Crée le nouvel utilisateur
            login(request, user)    # Le connecte directement
            return redirect('blog:home')
    else:
        form = RegisterForm()

    return render(request, 'blog/register.html', {'form': form})


# La connexion et la déconnexion sont gérées par LoginView et LogoutView
# de Django, déclarées dans urls.py (voir blog/urls.py).


def get_base_posts_queryset():
    """Helper pour charger les relations d'un coup (évite le problème N+1 requêtes)."""
    return Post.objects.filter(status='published').select_related(
        'author', 'category'
    ).prefetch_related('tags')


def home(request):
    posts_list = get_base_posts_queryset().order_by('-published_at')
    paginator = Paginator(posts_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog/home.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category').prefetch_related('tags'),
        slug=slug,
        status='published'
    )
    # --- GESTION DU COMPTEUR DE VUES SÉCURISÉ ---
    # Récupérer la liste des articles déjà vus par ce visiteur dans sa session
    viewed_posts = request.session.get('viewed_posts', [])

    # Si cet article n'a pas encore été vu pendant cette session
    if post.id not in viewed_posts:
        Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
        post.refresh_from_db()  # Met à jour la variable post avec la nouvelle valeur
        viewed_posts.append(post.id)
        request.session['viewed_posts'] = viewed_posts  # Sauvegarde la liste en session
        request.session.modified = True  # <-- INDISPENSABLE pour que la session s'enregistre !
    # --------------------------------------------

    comments = post.comments.filter(active=True).select_related('author')

    if request.method == 'POST':
        # Seuls les utilisateurs connectés peuvent commenter
        if not request.user.is_authenticated:
            return redirect(f"{resolve_url(settings.LOGIN_URL)}?next={request.path}")

        # L'auteur d'un article ne peut pas commenter son propre article
        if request.user == post.author:
            messages.error(request, "Vous ne pouvez pas commenter votre propre article.")
            return redirect('blog:post_detail', slug=post.slug)

        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts_list = get_base_posts_queryset().filter(
        category=category
    ).order_by('-published_at')

    paginator = Paginator(posts_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts,
    })


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts_list = get_base_posts_queryset().filter(
        tags=tag
    ).order_by('-published_at')

    paginator = Paginator(posts_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, 'blog/tag_detail.html', {
        'tag': tag,
        'posts': posts,
    })


def tags_list(request):
    tags = Tag.objects.all().order_by('name')
    return render(request, 'blog/tags_list.html', {'tags': tags})


def search(request):
    query = request.GET.get('q', '').strip()
    posts_list = get_base_posts_queryset().none()

    if query:
        posts_list = get_base_posts_queryset().filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        ).distinct().order_by('-published_at')

    paginator = Paginator(posts_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'blog/partials/search_results_partial.html', {
            'posts': posts,
            'query': query,
        })

    return render(request, 'blog/search_results.html', {
        'posts': posts,
        'query': query,
    })


def about(request):
    return render(request, 'blog/about.html')


# ---------------------------------------------------------------
# CRUD des articles pour les utilisateurs connectés
# ---------------------------------------------------------------

def generate_unique_slug(title):
    """Crée un slug à partir du titre, en garantissant son unicité."""
    base = slugify(title)[:100] or 'article'
    slug = base
    n = 2
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).select_related(
        'category'
    ).order_by('-created_at')
    return render(request, 'blog/my_posts.html', {'posts': posts})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = generate_unique_slug(post.title)
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            form.save_m2m()  # enregistre les tags
            messages.success(request, "Votre article a été créé.")
            if post.status == 'published':
                return redirect('blog:post_detail', slug=post.slug)
            return redirect('blog:my_posts')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'is_edit': False})


@login_required
def post_update(request, slug):
    # author=request.user : un utilisateur ne peut modifier que SES articles (sinon 404)
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            form.save_m2m()
            messages.success(request, "Votre article a été modifié.")
            if post.status == 'published':
                return redirect('blog:post_detail', slug=post.slug)
            return redirect('blog:my_posts')
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {
        'form': form,
        'is_edit': True,
        'post': post,
    })


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Votre article a été supprimé.")
        return redirect('blog:my_posts')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # enregistre le message dans la base : visible dans l'admin
            messages.success(request, "Merci ! Votre message a bien été envoyé.")
            return redirect('blog:contact')  # adaptez au nom de votre URL de contact
    else:
        form = ContactForm()
    return render(request, 'blog/contact.html', {'form': form})