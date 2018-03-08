"""
Concept model relations
-----------------------

These are direct reimplementations of Django model relations,
at the moment they onyl exist to make permissions-based filtering easier for
the GraphQL codebase. However, in future these may add additional functionality
such as automatically applying certain permissions to ensure users only
retrieve the right objects.

When building models that link to any subclass of ``_concept``, use these in place
of the Django builtins.

.. note:: The model these are place on does *not* need to be a subclass of concept.
 They are for linking *to* a concept subclass.

"""

from django.db.models import (
    ForeignKey, ManyToOneRel,
    ManyToManyField, ManyToManyRel,
    OneToOneField, OneToOneRel
)


class ConceptOneToOneRel(OneToOneRel):
    pass


class ConceptOneToOneField(OneToOneField):
    """
    Reimplementation of ``OneToOneField`` for linking
    a model to a Concept
    """
    rel_class = ConceptOneToOneRel


class ConceptManyToOneRel(ManyToOneRel):
    pass


class ConceptForeignKey(ForeignKey):
    """
    Reimplementation of ``ForeignKey`` for linking
    a model to a Concept
    """
    rel_class = ConceptManyToOneRel


class ConceptManyToManyRel(ManyToManyRel):
    pass


class ConceptManyToManyField(ManyToManyField):
    """
    Reimplementation of ``ManyToManyField`` for linking
    a model to a Concept
    """
    rel_class = ConceptManyToManyRel
