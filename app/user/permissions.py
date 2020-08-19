# from rest_framework.permissions import BasePermission, SAFE_METHODS


# class IsOwnerProfile(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         if request.user.id is not None:
#             return obj.user == request.user