from gras.model_types import get_model_types_of_app
from gras.admin import init_admins as _init_admins
from gras.serializers import init_serializers as _init_serializers
from gras.views import FactoryView
from django.conf.urls import url, include

def init_admins(app_name):
    _init_admins(get_model_types_of_app(app_name))

def init_serializers(app_name):
    _init_serializers(get_model_types_of_app(app_name))

def init_views(app_name):
    init_serializers(app_name)
    factory_views = FactoryView(get_model_types_of_app(app_name))
    factory_views.init_views()
    return factory_views.model_shunt

def init_urls(app_name, factory_views=None, version='v1'):
    factory_views = factory_views or init_views(app_name)
    urlpatterns = [        
        url(r'^%s/(?P<model>[a-zA-Z]\w*)/$'%version,
            factory_views, name='%s-api-%s-model-list'%(app_name, version)),
        url(r'^%s/(?P<model>[a-zA-Z]\w*)/(?P<pk>\d+)/$'%version,
            factory_views, name='%s-api-%s-model-detail'%(app_name, version)),        
    ]
    return urlpatterns
