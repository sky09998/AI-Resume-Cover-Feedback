from django.contrib import admin
from .models import Document, UserM, UserMAdmin, Contact, Order
from .models import APIRequestLog
from .models import UserActivityLog

admin.site.register(UserM)
admin.site.register(UserMAdmin)
admin.site.register(Document)
admin.site.register(Contact)
admin.site.register(Order)


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'request_type')
    list_filter = ('timestamp', 'request_type')
    search_fields = ('user__username',)

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'details')
    list_filter = ('activity_type', 'timestamp', 'user')
    search_fields = ('user__username', 'details', 'activity_type')
    readonly_fields = ('user', 'activity_type', 'timestamp', 'details')

    def has_add_permission(self, request):
        # Disable adding logs directly via admin
        return False

    def has_change_permission(self, request, obj=None):
        # Disable editing logs directly via admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Optionally disable deletion, or enable as needed
        return False