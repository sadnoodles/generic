# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from gras.models import CommonAttrBase, CommonAttr
from django.apps import apps
from gras.registers import AppModelRegister


def filter_id(model):
    all_field = []
    all_db_field = []
    normal_field = []
    foreign_field = []
    for field in model._meta.fields:
        if field.is_relation:
            foreign_field.append(field.name)
            all_db_field.append(field.attname)
        else:
            normal_field.append(field.name)
            all_db_field.append(field.name)
        all_field.append(field.name)

    return all_field, all_db_field, normal_field, foreign_field


class TypeAttr:
    'Store all attributes of a model, include model, serializer and some other settings.'

    def __init__(self, model=None, model_name=None):
        self.model = model
        self.model_name = model_name
        self.serializer = None
        self.auto_serializer = None
        self.all_fields = []
        self.all_db_fields = []
        self.normal_fields = []
        self.foreign_keys = []
        self.filter_fields = []
        self.mixins = []  
        if self.model:
            self.filter_id(self.model)
        self.get_filter_fields()

    def filter_id(self, model):
        (
            self.all_fields,
            self.all_db_fields,
            self.normal_fields,
            self.foreign_keys
        ) = filter_id(model)
    
    def get_filter_fields(self):
        filter_fields = self.all_fields

        if self.model.PreSetting.filter_include_fields:
            filter_fields = [i for i in self.model.PreSetting.filter_include_fields  if i in self.all_fields]

        if self.model.PreSetting.filter_exclude_fields:
            filter_fields = [i for i in filter_fields if i not in self.model.PreSetting.filter_exclude_fields]

        self.filter_fields = filter_fields
        return self.filter_fields

    def exists(self):
        return (self.model is not None) and (self.serializer is not None)


def get_model_types_of_app(app_name):
    # cache model_types for app_name
    if AppModelRegister.get(app_name, None):
        return AppModelRegister.get(app_name)

    model_types = {}
    _models = apps.all_models[app_name]
    for model_name, obj in _models.items():
        if not issubclass(obj, CommonAttrBase):
            continue

        if getattr(obj._meta, 'abstract', False) or not getattr(obj._meta, 'managed', True):
            continue

        model_types[model_name] = TypeAttr(obj, model_name)
        type_attr = model_types[model_name]
        
        if hasattr(obj, "verbose_name_plural"):
            obj._meta.verbose_name_plural = u"%s (%s)" % (
                obj.verbose_name_plural, obj._meta.verbose_name_plural)
        setattr(obj, 'type_attr', type_attr)  # quick access
    
    AppModelRegister.register_kv(app_name, model_types)
    return model_types


