from django.db import migrations


def populate_db(apps, *_ignored):
    datatype = apps.get_model('wikibase', 'Datatype')
    datatype(class_name='UserValue').save()


class Migration(migrations.Migration):
    dependencies = [
        ('wikibase', '0003_uservalue'),
    ]

    operations = [
        migrations.RunPython(populate_db),
    ]
