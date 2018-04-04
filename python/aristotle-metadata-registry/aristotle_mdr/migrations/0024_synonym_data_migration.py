# Custom migration for synonym data
from django.db import migrations

def add_slots(apps, schema_editor):

    installed = 'aristotle_mdr_slots' in apps.all_models.keys()
    print('installed is %s'%installed)
    if True:
        slot = apps.get_model('aristotle_mdr_slots', 'Slot')
        _concept = apps.get_model('aristotle_mdr', '_concept')

        # s=slot.objects.create(
        #     name='Synonyms',
        #     concept=_concept.objects.first(),
        #     value='Blah'
        # )
        # print(s)

        for concept in _concept.objects.all():
            if concept.synonyms:
                print('added one')
                slot.objects.create(
                    name='Synonyms',
                    concept=concept,
                    value=concept.synonyms
                )

def reverse_add_slots(apps, schema_editor):

    installed = apps.is_installed('aristotle_mdr.contrib.slots')

    if installed:
        slot = apps.get_model('aristotle_mdr_slots', 'Slot')
        for s in slot.objects.all():
            if s.name == 'Synonyms' and len(s.value) < 200:
                s.concept.synonyms = s.value
                s.concept.save()

class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0023_auto_20180206_0332'),
    ]

    operations = [
        migrations.RunPython(add_slots, reverse_add_slots),
    ]
