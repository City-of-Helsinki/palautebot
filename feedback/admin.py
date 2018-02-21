from django.contrib import admin

from .models import DirectMessage, Feedback, Tweet

admin.site.register(DirectMessage)
admin.site.register(Feedback)
admin.site.register(Tweet)
