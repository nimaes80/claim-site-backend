from django.contrib import admin

from account.models import SystemSetting, User, ContactUs, FAQ, GlobalInfo
from solo.admin import SingletonModelAdmin

admin.site.register(User)
admin.site.register(SystemSetting, SingletonModelAdmin)
admin.site.register(ContactUs)
admin.site.register(FAQ)
admin.site.register(GlobalInfo)
