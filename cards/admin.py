from django.contrib import admin
from .models import UserCategory, User, Card, UserCard, Transaction, TransactionCategory

# change admin site name
admin.site.site_header = "Gestione Tessere"
admin.site.site_title = "Card Management Admin"
admin.site.index_title = "Welcome to Card Management Admin"

@admin.register(UserCategory)
class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name', 'created_at', 'updated_at')

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('name', 'surname', 'gender', 'category', 'created_at', 'updated_at')
#     search_fields = ('name', 'surname')
#     ordering = ('name', 'surname')
#     list_filter = ('gender', 'category', 'created_at', 'updated_at')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_number', 'printed', 'created_at', 'updated_at', 'user')
    search_fields = ('card_number', 'id')
    ordering = ('-created_at', )
    list_filter = ('printed', 'created_at', 'updated_at', )

    def user(self, obj):
        user_card = UserCard.objects.filter(card=obj).first()
        return user_card.user if user_card else None



# @admin.register(UserCard)
# class UserCardAdmin(admin.ModelAdmin):
#     list_display = ('user', 'card', 'status', 'created_at', 'updated_at')
#     search_fields = ('user__name', 'user__surname', 'card__card_number')
#     ordering = ('user__name', 'user__surname')
#     list_filter = ('status', 'created_at', 'updated_at', 'created_by')

# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ('user_id', 'card_id', 'amount', 'notes', 'category', 'created_at', 'updated_at')
#     search_fields = ('user__name', 'user__surname', 'card__card_number', 'notes')
#     ordering = ('-created_at',)
#     list_filter = ('category', 'created_at', 'updated_at', 'created_by')


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name', 'created_at', 'updated_at')



from import_export import resources
from import_export.admin import ImportExportModelAdmin

class UserResource(resources.ModelResource):
    class Meta:
        model = User

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_classes = [UserResource]
    list_display = ('name', 'surname', 'gender', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'surname')
    ordering = ('name', 'surname')
    list_filter = ('gender', 'category', 'created_at', 'updated_at')

class UserCardResource(resources.ModelResource):
    class Meta:
        model = UserCard
        fields = ('user__name', 'user__surname','card__card_number', 'card__id', 'status', 'created_at', 'updated_at')

@admin.register(UserCard)
class UserCardAdmin(ImportExportModelAdmin):
    resource_classes = [UserCardResource]
    list_display = ('user', 'card', 'status', 'created_at', 'updated_at')
    search_fields = ('user__name', 'user__surname', 'card__card_number')
    ordering = ('user__name', 'user__surname')
    list_filter = ('status', 'created_at', 'updated_at', 'created_by')


class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction
        # fields = ('user_id', 'card_id', 'amount', 'notes', 'category', 'created_at', 'updated_at')
        fields = ('user_id__name', 'user_id__surname', 'card_id__card_number', 'amount', 'notes', 'category__name', 'created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    resource_classes = [TransactionResource]
    list_display = ('user_id', 'card_id', 'amount', 'notes', 'category', 'created_at', 'updated_at')
    search_fields = ('user__name', 'user__surname', 'card__card_number', 'notes')
    ordering = ('-created_at',)
    list_filter = ('category', 'created_at', 'updated_at', 'created_by')

