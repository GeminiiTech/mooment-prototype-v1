from django.contrib import admin
from .models import MyUser,GoogleOAuthToken


# Register your models here.

admin.site.register(MyUser)
admin.site.register(GoogleOAuthToken)
