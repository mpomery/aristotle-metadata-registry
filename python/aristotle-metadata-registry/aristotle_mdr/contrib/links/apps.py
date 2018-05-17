from django.apps import AppConfig


class Config(AppConfig):
    name = 'aristotle_mdr.contrib.links'
    label = 'aristotle_mdr_links'
    verbose_name = 'Aristotle Concept Links and Relations'
    description = """
    This module allows users of the registry to create taxonomies using custom relationships with associated roles,
    which can be used to create links between metadata items.

    For example, a user could create a "Broader than" relationship, with "broader term" and "narrower term" as the roles within the relationship.
    A new link could be made based on this relationship with the broader term end connecting to the Object Class "Person" and the narrower term end pointing to the Object Class "Employee".
    """
