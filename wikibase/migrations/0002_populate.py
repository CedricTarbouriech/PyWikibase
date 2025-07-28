from django.db import migrations


def populate_db(apps, *_ignored):
    datatype = apps.get_model('wikibase', 'Datatype')
    datatype(class_name='Item').save()
    datatype(class_name='Property').save()
    datatype(class_name='StringValue').save()
    datatype(class_name='UrlValue').save()
    datatype(class_name='QuantityValue').save()
    datatype(class_name='TimeValue').save()
    datatype(class_name='GlobeCoordinatesValue').save()
    datatype(class_name='MonolingualTextValue').save()


class Migration(migrations.Migration):
    dependencies = [
        ('wikibase', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_db),
    ]
