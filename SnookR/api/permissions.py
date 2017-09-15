from rest_framework import permissions


class TeamPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.user_permissions.filter(codename='add_team').exists()
        else:
            return True


class TeamInvitePermission(TeamPermission):
    """The same people that can make teams can also make invites"""
