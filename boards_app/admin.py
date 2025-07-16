from django.contrib import admin
from .models import Board
# Register your models here.

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface for the Board model.

    Includes:
    - Custom list display and filtering
    - Permissions based on user roles (owner or staff)
    - Automatic setting of owner and member data on creation
    - Read-only logic for computed fields
    """

    list_display = ('id', 'title', 'owner_id', 'member_count', 'ticket_count', 
                    'tasks_to_do_count', 'tasks_hight_prio_count')
    search_fields = ('title',)
    list_filter = ('owner_id',)
    ordering = ('-id',)
    
    def get_queryset(self, request):
        """
        Optimize queryset by preloading the related owner.
        """
        qs = super().get_queryset(request)
        return qs.select_related('owner_id')
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Member Count'
    def ticket_count(self, obj):
        return obj.ticket_count
    ticket_count.short_description = 'Ticket Count'
    def tasks_to_do_count(self, obj):
        return obj.tasks_to_do_count
    tasks_to_do_count.short_description = 'Tasks To Do Count'
    def tasks_hight_prio_count(self, obj):
        return obj.tasks_hight_prio_count
    tasks_hight_prio_count.short_description = 'High Priority Tasks Count'
    def owner_id(self, obj):
        return obj.owner_id.fullname if obj.owner_id else 'No Owner'
    owner_id.short_description = 'Owner'
    def has_add_permission(self, request):
        return request.user.is_authenticated and request.user.is_staff
    def has_change_permission(self, request, obj=None):
        """
        Allow staff or the board owner to change the board.
        """
        if obj is None:
            return request.user.is_authenticated and request.user.is_staff
        return request.user.is_authenticated and (request.user.is_staff or request.user == obj.owner_id)
    def has_delete_permission(self, request, obj=None):
        """
        Allow staff or the board owner to delete the board.
        """
        if obj is None:
            return request.user.is_authenticated and request.user.is_staff
        return request.user.is_authenticated and (request.user.is_staff or request.user == obj.owner_id)
    def has_view_permission(self, request, obj=None):
        """
        Allow staff or the board owner to view the board.
        """
        if obj is None:
            return request.user.is_authenticated
        return request.user.is_authenticated and (request.user.is_staff or request.user == obj.owner_id)
    def save_model(self, request, obj, form, change):
        """
        Set ownership and initialize counters when creating a board.
        Also adds the creator as a member.
        """
        if not change:
            obj.owner_id = request.user
            obj.member_count = 1
            obj.ticket_count = 0
            obj.tasks_to_do_count = 0
            obj.tasks_hight_prio_count = 0
        obj.save()
        if 'members' in form.cleaned_data:
            members = form.cleaned_data['members']
            obj.members.set(members + [request.user])
            obj.member_count = obj.members.count()
            obj.save()
        else:
            obj.members.add(request.user)
            obj.member_count = 1
            obj.save()
    def delete_model(self, request, obj):
        """
        Delete the board only if the user is staff or the owner.
        """
        if request.user.is_authenticated and (request.user.is_staff or request.user == obj.owner_id):
            obj.delete()
        else:
            raise PermissionError("You do not have permission to delete this board.")
    def get_readonly_fields(self, request, obj=None):
        """
        Make counters and ownership read-only for existing boards.
        """
        if obj is None:
            return []
        return ['owner_id', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_hight_prio_count']
    def get_fields(self, request, obj=None):
        """
        Show the 'members' field only during creation.
        """
        fields = super().get_fields(request, obj)
        if obj is None:
            fields.append('members')
        return fields
    def get_form(self, request, obj=None, **kwargs):
        """
        Make 'members' optional when creating a board.
        """
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields['members'].required = False
        return form
