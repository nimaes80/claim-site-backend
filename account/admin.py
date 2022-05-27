from django.contrib import admin

from account.models import SystemSetting, User
from solo.admin import SingletonModelAdmin

admin.site.register(User)
admin.site.register(SystemSetting, SingletonModelAdmin)
