#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin

def init_admin_class(ta, admincls=None, **kwargs):

    if admincls is None:
        admincls = admin.ModelAdmin
        cls_name = ta.model.__name__ + 'Admin'
    else:
        cls_name = admincls.__name__

    def add_list(name, ls, insert=False):
        ret = list(ls)
        for i in reversed(getattr(admincls, name, [])):
            if i not in ret:
                if insert:
                    ret.insert(0, i)
                else:
                    ret.append(i)

        for i in reversed(kwargs.get(name, [])):
            if i not in ret:
                if insert:
                    ret.insert(0, i)
                else:
                    ret.append(i)

        return tuple(ret)

    def filter_fields(ls):
        for i in ls:
            if isinstance(i, str):
                if i.startswith('__'):
                    yield i
                if i in ta.all_fields:
                    yield i
            else:
                yield i

    list_filter = ['deleted', 'update_date', 'status']
    search_fields = ('id', 'uuid')
    search_fields = add_list("search_fields", search_fields)
    readonly_fields = ta.model.PreSetting.admin_readonly_fields + ['uuid', "author" ]
    readonly_fields = add_list("readonly_fields", readonly_fields)
    inlines = []
    inlines = add_list("inlines", inlines)
    list_display = ['id', 'tag_list', 'update_date', 'create_date']
    list_display = add_list("list_display", list_display, True)
    raw_id_fields = ta.foreign_keys
    raw_id_fields = add_list("raw_id_fields", raw_id_fields)
    

    attr_dict = {
        'list_filter': tuple(filter_fields(list_filter)),
        'search_fields': tuple(filter_fields(search_fields)),
        'readonly_fields': tuple(filter_fields(readonly_fields)),
        'inlines': inlines,
        'list_display': tuple(filter_fields(list_display)),
        'list_per_page': 20,
        'show_full_result_count': False,
    }

    bases = (admincls, )
    if ta.mixins:
        bases =  kwargs.get("bases", ()) + tuple(ta.mixins) + bases

    new_admincls = type(
        cls_name,
        bases,
        attr_dict
    )
    return new_admincls


def wrap_admin_register(func):

    def register(cls, admincls=None, *arg, **kwargs):
        
        admincls = init_admin_class(cls.type_attr, admincls, **kwargs)
        return func(cls, admincls, *arg, **kwargs)

    return register

admin_site_register = wrap_admin_register(admin.site.register)

def init_admins(model_types, skip_list=()):

    for name, m in model_types.items():
        if name in skip_list or admin.site.is_registered(m.model):
            continue

        raw_id_fields = m.foreign_keys
        
        admin_site_register(
            m.model,
            raw_id_fields=raw_id_fields,
            mixins=m.mixins)


