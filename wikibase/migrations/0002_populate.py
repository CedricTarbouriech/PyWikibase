from django.db import migrations


def populate_db(apps, *_ignored):
    Datatype = apps.get_model('wikibase', 'Datatype')
    Datatype(class_name='Item').save()
    Datatype(class_name='Property').save()
    Datatype(class_name='StringValue').save()
    Datatype(class_name='QuantityValue').save()
    Datatype(class_name='UnitQuantityValue').save()
    Datatype(class_name='TimeValue').save()
    Datatype(class_name='GlobeCoordinatesValue').save()
    Datatype(class_name='MonolingualTextValue').save()
    Datatype(class_name='UrlValue').save()


class Migration(migrations.Migration):

    dependencies = [
        ('wikibase', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_db),
    ]
