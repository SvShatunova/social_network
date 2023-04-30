from django.contrib import admin

from .models import Group, Post, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    date_hierarchy = 'pub_date'
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    list_display_links = ('pk', 'title',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'created')
    search_fields = ('author', 'text')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = '-пусто-'
