#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework import exceptions
from gras.model_types import TypeAttr
import traceback
from gras.registers import FactorySerializerMixinRegister

readonly_fields = ('create_date', 'uuid', 'author') 

filter_fields = []


class ForceCleanMixin(object):
    
    def is_valid(self, raise_exception=False):

        ret = super(ForceCleanMixin, self).is_valid(
            raise_exception=raise_exception)
        if not ret:
            return ret

        ModelClass = self.Meta.model
        validated_data = dict(self._validated_data)

        info = serializers.model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                serializers.set_many(instance, field_name, value)

        def format_VE(exc):
            msg = {}
            if hasattr(exc, "error_dict"):
                for k, v in exc.error_dict.items():
                    msg[k] = [i.message for i in v]
            elif hasattr(exc, "error_list"):
                msg["__all__"] = [i.message for i in exc.error_list]
            return msg
        try:
            instance.clean()
        except ValidationError as exc:
            self._errors = format_VE(exc)
        else:
            self._errors = []

        if self._errors and raise_exception:
            raise exceptions.ValidationError(self.errors)

        for field in ModelClass.PreSetting.automatic_fields:
            self._validated_data[field] = getattr(instance, field)
        
        return not bool(self._errors)

class ModifyMixin(ForceCleanMixin):

    def api_fields(self):
        d = self.data.copy()  # keep order
        model = self.Meta.model
        if not hasattr(model, "PreSetting"):
            return d
        blocked = model.PreSetting.api_block_fields
        for i in self.data.keys():
            if i in blocked:
                d.pop(i)
        return d

    def to_internal_value(self, data):
        ret = super(ModifyMixin, self).to_internal_value(data)
        return ret


def init_serializer(ta):
    all_fields = ta.all_fields
    model = ta.model

    _read_onlys = []
    extra_kwargs = {}
    if not hasattr(model, "PreSetting"):
        _read_onlys = readonly_fields
    else:
        _read_onlys = readonly_fields + tuple(model.PreSetting.api_block_fields)
        for i in model.PreSetting.api_block_fields:
            extra_kwargs[i] = {"write_only":True}

    bases =  FactorySerializerMixinRegister.merge_default_bases(
        ta.model_name, (ModifyMixin, serializers.ModelSerializer, ))

    attrs = {
            "id": serializers.IntegerField(required=False),
            'Meta': type('Meta', (), {
                'model': model,
                'fields': all_fields,
                'read_only_fields': tuple([i for i in all_fields if i in _read_onlys]),
            })
    }


    ta.serializer = type(
        ta.model.__name__ + 'Serializer',
        bases,
        attrs
    )

    ta.auto_serializer = ta.serializer

    return ta.serializer

def init_serializers(model_types):
    
    for name, type_attr in model_types.items():
        if type_attr.serializer is None:
            type_attr.serializer = init_serializer(type_attr)
    return model_types

def get_serializer_by_name(model_types, name):
    return model_types.get(name, TypeAttr()).serializer
