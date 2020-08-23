from rest_framework import viewsets, mixins, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Tag, Ingredient
from recipe import serializers


class BaseRecipeAttrViewset(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base Viewset for user owned recipe attributes"""
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        """Return objects for the current authenticated user"""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewset):
    """Manage Tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewset):
    """Manage Ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
