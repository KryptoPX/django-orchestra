from django.contrib.contenttypes.fields import GenericRelation
from django.db import DEFAULT_DB_ALIAS


class VirtualDatabaseRelation(GenericRelation):
    """ Delete related databases if any """
    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        pks = []
        for obj in objs:
            if obj.database_id:
                pks.append(obj.database_id)
        if not pks:
            return []
        return self.remote_field.model._base_manager.db_manager(using).filter(pk__in=pks)
