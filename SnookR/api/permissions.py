from rest_framework import permissions


class TeamPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.user_permissions.filter(codename='add_team').exists()
        else:
            return True


class TeamInvitePermission(TeamPermission):
    """The same people that can make teams can also make invites"""


class MessagePermission(permissions.BasePermission):
    message = 'Users can only see their own messages.'

    def has_object_permission(self, request, view, obj):
        return obj.receiver == request.user or obj.sender == request.user