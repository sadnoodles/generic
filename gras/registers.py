# -*- coding: utf-8 -*-

from collections import defaultdict

def register_factory(name, extra=None):

    '''
    '''

    def get(cls, name, default=None):
        return cls.registed_class.get(name, default)

    def merge_default(cls, name, default=()):
        mixins = cls.registed_class.get(name, [])
        return tuple(mixins) + (default or ())

    kls =  type(name, (object, ), dict(
        registed_class=defaultdict(list),
        get=classmethod(get),
        merge_default_bases=classmethod(merge_default)
    ))

    def register(kls, *aliases):
        def dec(cls):
            for alias in aliases:
                kls.registed_class[alias].insert(0, cls)
            return cls
        return dec

    def register_kv(kls, k, v):
        kls.registed_class[k] = v
        return 

    kls.register = classmethod(register)
    kls.register_kv = classmethod(register_kv)
    return kls

# Global registers
FactoryListViewMixinRegister = register_factory('FactoryListViewMixinRegister')
FactoryDetailViewMixinRegister = register_factory('FactoryDetailViewMixinRegister')
FactorySerializerMixinRegister = register_factory('FactorySerializerMixinRegister')

AppModelRegister = register_factory('AppModelRegister')


