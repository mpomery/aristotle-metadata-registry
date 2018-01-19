from django.contrib import admin


from aristotle_mdr.contrib.links import models as links

from aristotle_mdr.register import register_concept


class RoleRelationInline(admin.TabularInline):
    model = links.RelationRole
    fields = ("ordinal", "name", "definition", "multiplicity",)
    extra = 1


register_concept(
    links.Relation,
    extra_fieldsets=[('Extra details', {'fields': ['arity']})],
    extra_inlines=[RoleRelationInline],
    reversion={
        'follow': ['relationrole_set'],
        'follow_classes': [links.RelationRole]
    }
)
