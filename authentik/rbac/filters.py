"""RBAC API Filter"""
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework_guardian.filters import ObjectPermissionsFilter


class ObjectFilter(ObjectPermissionsFilter):
    """Object permission filter that grants global permission higher priority than
    per-object permissions"""

    def filter_queryset(self, request: Request, queryset: QuerySet, view) -> QuerySet:
        permission = self.perm_format % {
            "app_label": queryset.model._meta.app_label,
            "model_name": queryset.model._meta.model_name,
        }
        # having the global permission set on a user has higher priority than
        # per-object permissions
        if request.user.has_perm(permission):
            return queryset
        queryset = super().filter_queryset(request, queryset, view)
        if not queryset.exists():
            # User doesn't have direct permission to all objects
            # and also no object permissions assigned (directly or via role)
            raise PermissionDenied()
        return queryset
