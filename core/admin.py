from django.contrib import admin
from .models import Staller, MenuItems, Category, Subcat, Egit, Following, Rating, Foo_Category, New_offer, Order, Cart, CartItem, Loccat
from embed_video.admin import AdminVideoMixin


class MyModelAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass


# Combined StallerAdmin class
class StallerAdmin(MyModelAdmin):
    list_display = ['name', 'owner', 'address', 'contact', 'timings', 'rating', 'latitude', 'longitude']
    filter_horizontal = ('category',)  # Make sure to use 'category' as the related name in your model

    # You can add other configurations, if necessary, like search fields, ordering, etc.
    search_fields = ['name', 'address', 'contact']
    ordering = ['name']  # Just an example, you can set your own ordering


# Register the models with their respective admin classes
admin.site.register(Staller, StallerAdmin)
admin.site.register(MenuItems)
admin.site.register(Egit)
admin.site.register(Category)
admin.site.register(Subcat)
admin.site.register(Following)
admin.site.register(Rating)
admin.site.register(Foo_Category)
admin.site.register(New_offer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Loccat)