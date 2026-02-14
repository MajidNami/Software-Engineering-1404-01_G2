from django.contrib import admin
from .models import Article, Version, Tag, Vote

admin.site.register(Article)
admin.site.register(Version)
admin.site.register(Tag)
admin.site.register(Vote) 
