from django.contrib import admin
from django.db.models import get_model


class AssociationAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'identifier', 'avatar', 'is_active']


admin.site.register(get_model('social_registration', 'association'), AssociationAdmin)


