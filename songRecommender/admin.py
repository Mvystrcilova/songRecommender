from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here

# uzivatelsky jmeno: m_vys
# heslo: centropen

from .models import Song, List, Song_in_List, Played_Song, Distance_to_List, Distance_to_User, Distance, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


class SongAdmin(admin.ModelAdmin):
    pass


class ListAdmin(admin.ModelAdmin):
    pass


class Song_in_ListAdmin(admin.ModelAdmin):
    pass


class Played_SongAdmin(admin.ModelAdmin):
    pass


class DistanceAdmin(admin.ModelAdmin):
    pass


class Distance_to_UserAdmin(admin.ModelAdmin):
    pass


class Distance_to_ListAdmin(admin.ModelAdmin):
    pass


admin.site.register(List, ListAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Song_in_List, Song_in_ListAdmin)
admin.site.register(Played_Song, Played_SongAdmin)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(Distance_to_List, Distance_to_ListAdmin)
admin.site.register(Distance_to_User, Distance_to_UserAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
