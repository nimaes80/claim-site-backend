from rest_framework.permissions import BasePermission

from utils.utils import getattrd


class IsAdminOrExactUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj


class IsAdminOrCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.creator == request.user


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff

    def has_permission(self, request, view):
        return request.user.is_staff


class IsCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsCreatorLawyer(BasePermission):
    def has_object_permission(self, request, view, obj):
        lawyer = getattrd(self.request, "user.lawyer", None)
        return lawyer and obj.creator == lawyer


class IsLawyer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(getattrd(self.request, "user.lawyer", None))


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.active_company
            and request.user.active_company.creator == request.user
        )
