# -*- coding: utf-8 -*-

import warnings
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import django_filters
from gras.registers import FactoryListViewMixinRegister, FactoryDetailViewMixinRegister

class DjangoViewModelPermissions(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class DjangoViewModelListPermissions(DjangoViewModelPermissions):
    def has_permission(self, request, view):
        has_list_perm = super(DjangoViewModelListPermissions,
                              self).has_permission(request, view)
        return has_list_perm and request.user.is_staff


class APIFieldOnlyMixin(object):
    """
    Retrieve a model instance, only API allowed fields.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.api_fields())


def filter_factory(model_name, _model, filter_fields):
    class Meta:
        model = _model
        fields = {
            field: [
                'isnull',
                'gt',
                'in',
                'exact',
                'lt',
            ] for field in filter_fields
            # need to filter file and blob fields.
        }

    return type(
        model_name + "Filter",
        (django_filters.FilterSet, ),
        {"Meta": Meta}
    )


def init_list_view(ta, mixins=None):
    mixins = mixins or ()
    bases = (generics.ListCreateAPIView, )
    bases = mixins + bases
    return type(
            ta.model.__name__ + 'ListAPIView',
            bases,
            {
                "queryset": ta.model.objects.all().order_by('-id'),
                "permission_classes": (DjangoViewModelListPermissions, ),
                "serializer_class": ta.serializer,
                "filter_class": filter_factory(ta.model.__name__, ta.model, ta.filter_fields),
                "search_fields": ('=tags__name',),
                "filter_fields": ta.filter_fields
            }
        )

def init_detail_view(ta, mixins=None):
    mixins = mixins or ()
    bases = (
                APIFieldOnlyMixin,
                generics.RetrieveUpdateDestroyAPIView,
            )
    bases = mixins + bases
    return type(
            ta.model.__name__ + 'RetrieveUpdateDestroyAPIView',
            bases,
            {
                "queryset": ta.model.objects.all(),
                "permission_classes": (DjangoViewModelPermissions, ),
                "serializer_class": ta.serializer,
                "ordering_fields": 'id',
            }
        )


class NotFoundView(views.APIView):
    def get(self, request, model, pk, format=format):
        return Response(
            {"detail": "{} is not a avaliable source.".format(model)},
            status=status.HTTP_404_NOT_FOUND)


not_found_view = NotFoundView.as_view()

class FactoryView(object):
    
    def __init__(self, model_types):

        self.model_types = model_types
        self.model_list_views = {}
        self.model_detail_views = {}
        self.list_urls_map = {}
        self.detail_urls_map = {}

    def init_view_and_routers(self, model_types):
        for name, type_attr in model_types.items():
            if name in self.model_detail_views:
                continue
            
            mixins = FactoryDetailViewMixinRegister.get(name, [])
            self.model_detail_views[name] = init_detail_view(type_attr, mixins=tuple(mixins))

        for name, type_attr in model_types.items():
            if name in self.model_list_views:
                continue
            
            mixins = FactoryListViewMixinRegister.get(name, [])
            self.model_list_views[name] = init_list_view(type_attr, mixins=tuple(mixins))

        for name, view in self.model_detail_views.items():
            self.detail_urls_map[name] = view.as_view()

        for name, view in self.model_list_views.items():
            self.list_urls_map[name] = view.as_view()

    def init_views(self):
        self.init_view_and_routers(self.model_types)
        
    @csrf_exempt
    def model_shunt(self, request, model, pk=None, format=None):

        # Dynamically map urls. If setting changed, url changes too.
        if getattr(settings, 'STRICT_SAFE_MODE_API', False) and request.method not in ["GET", "HEAD", "OPTIONS"]:
            return not_found_view(request, model, pk=pk, format=format)

        if not model in self.detail_urls_map or \
                not self.model_types.get(model):
            return not_found_view(request, model, pk=pk, format=format)
        elif pk is None:
            return self.list_urls_map[model](request, format=format)
        else:
            return self.detail_urls_map[model](request, pk=pk, format=format)

