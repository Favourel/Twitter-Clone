from django.contrib import admin
from .models import Story, UserStat, User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')
    search_fields = ('username', 'email')


class UserStatAdmin(admin.ModelAdmin):
    list_display = ("user", "account_visit", "account_engaged")
    search_fields = ['user']


admin.site.register(User, UserAdmin)
admin.site.register(Story)
admin.site.register(UserStat, UserStatAdmin)
