from django.contrib import admin
from .models import FXTransaction, CurrencyPair, UserCurrencyPreference

class CurrencyPairAdmin(admin.ModelAdmin):
    list_display = ('input_currency', 'output_currency')
    search_fields = ('input_currency', 'output_currency')

class UserCurrencyPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'decimal_places')  # Display user and global decimal preference
    list_filter = ('decimal_places',)  # Filter by decimal preference
    search_fields = ('user__username',)
    filter_horizontal = ('preferred_pairs',)  # For selecting multiple currency pairs

# Register your models here.
admin.site.register(FXTransaction)
admin.site.register(CurrencyPair, CurrencyPairAdmin)
admin.site.register(UserCurrencyPreference, UserCurrencyPreferenceAdmin)
