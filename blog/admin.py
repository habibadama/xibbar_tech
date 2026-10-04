from django.contrib import admin
from .models import Category, ContactMessage, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views_count', 'published_at')
    list_filter = ('status', 'category', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('author__username', 'author__email', 'content')
    actions = ['approve_comments', 'disapprove_comments']

    @admin.action(description="Approuver les commentaires sélectionnés")
    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Désactiver les commentaires sélectionnés")
    def disapprove_comments(self, request, queryset):
        queryset.update(active=False)


 
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'apercu', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    list_editable = ('is_read',)
    actions = ['mark_as_read', 'mark_as_unread']
 
    @admin.display(description="Message")
    def apercu(self, obj):
        return obj.message[:60] + ('…' if len(obj.message) > 60 else '')
 
    @admin.action(description="Marquer comme lu")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
 
    @admin.action(description="Marquer comme non lu")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
 