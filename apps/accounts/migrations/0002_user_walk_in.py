from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_walk_in',
            field=models.BooleanField(
                default=False,
                verbose_name='Cadastro rápido (sem senha)',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='staff_notes',
            field=models.TextField(blank=True, verbose_name='Anotações internas da equipe'),
        ),
    ]