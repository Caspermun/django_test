from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


from blog.models import Post, Author, Category, Comment, CustomUser, Ad


# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': (
                'is_verified', 'is_active', 'is_staff', 'is_premium', 'is_superuser', 'groups',
                'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(Post)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Comment)


class Ads(admin.ModelAdmin):
    def image_tag(self, obj):
        return mark_safe('<img src="/media/%s" width="100" height="100" />' % (obj.image))

    image_tag.allow_tags = True
    image_tag.__name__ = 'Image'
    fieldsets = ((None, {'fields': ('title', 'description', 'image_tag', 'image', 'price', 'discount', 'user', 'moderated', 'is_active')}),)
    list_display = ('image_tag', 'title', 'user', 'is_active', 'moderated')
    list_display_links = ('image_tag', 'title')
    list_filter = ['user', 'created_at']
    search_fields = ('title__startswith', 'description__startswith')
    readonly_fields = ('image_tag',)
    list_per_page = 10


admin.site.register(Ad, Ads)
