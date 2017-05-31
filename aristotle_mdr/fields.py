from django.db.models import (
    ForeignKey, ManyToOneRel,
    ManyToManyField, ManyToManyRel,
    OneToOneField, OneToOneRel
)


class ConceptOneToOneRel(OneToOneRel):
    pass


class ConceptOneToOneField(OneToOneField):
    rel_class = ConceptOneToOneRel


class ConceptManyToOneRel(ManyToOneRel):
    pass


class ConceptForeignKey(ForeignKey):
    rel_class = ConceptManyToOneRel


class ConceptManyToManyRel(ManyToManyRel):
    pass


class ConceptManyToManyField(ManyToManyField):
    rel_class = ConceptManyToManyRel
