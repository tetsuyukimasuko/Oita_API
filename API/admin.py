# Register your models here.
from .models import Tenant, User, ClientInfo, Transaction
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username','billing_target', 'watson_id','watson_pass','is_monitor')
 
 
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)

class MyUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('billing_target','client','watson_id','watson_pass','login_status','is_active')}),
        (_('Permissions'), {'fields': ('is_monitor', 'is_superuser')})
    )
    list_filter=()
    list_display = ('username','billing_target', 'client','is_monitor')
    search_fields = ('username',)
    filter_horizontal = ()

    #add_form = MyUserCreationForm
    form = MyUserChangeForm

admin.site.register(User, MyUserAdmin)
admin.site.register(Tenant)
admin.site.register(ClientInfo)
admin.site.register(Transaction)