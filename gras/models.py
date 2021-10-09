from django.db import models

# Create your models here.

class AuthorMixin(models.Model):
    author = models.ForeignKey('auth.User', verbose_name="Author", default=-1, null=True, on_delete=models.SET_NULL)
    class Meta:
        abstract = True


class DateMixin(models.Model):
    create_date = models.DateTimeField(u"Create date", auto_now_add=True, db_index=True)
    update_date = models.DateTimeField(u"Update date", auto_now=True, db_index=True)
    class Meta:
        abstract = True


class MarkDeleteMixin(models.Model):
    deleted = models.BooleanField(u'Deleted mark', default=False, db_index=True)
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        # Mark delete
        self.deleted = True
        return super(self.__class__, self).save()

class CommonAttrBase(models.Model):
    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        abstract = True

    class PreSetting:
        api_block_fields = [] 
        admin_readonly_fields = []
        automatic_fields = []

class CommonAttr(DateMixin, CommonAttrBase):
    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        abstract = True

class CommonAttrPlus(MarkDeleteMixin, AuthorMixin, DateMixin, CommonAttrBase):
    
    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        abstract = True
