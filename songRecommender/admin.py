from django.contrib import admin

# Register your models here

# uzivatelsky jmeno: m_vys
# heslo: 1f2r4ijls85

from .models import Song, List, Song_in_List, Played_Song, Distance_to_List, Distance_to_User, Distance


# admin.site.register(Song)
# admin.site.register(List)
# admin.site.register(Song_in_List)
# admin.site.register(Played_Song)
# admin.site.register(Distance)
# admin.site.register(Distance_to_User)
# admin.site.register(Distance_to_List)

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
