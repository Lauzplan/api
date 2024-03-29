# Generated by Django 3.2.2 on 2021-05-16 12:09

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.polygon
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_db_constraints.operations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nom')),
                ('geometry', django.contrib.gis.db.models.fields.PolygonField(default=django.contrib.gis.geos.polygon.Polygon(), srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='CultivatedArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField(verbose_name='Label de la culture')),
                ('is_active', models.BooleanField(default=True)),
                ('harvest_date', models.DateField(null=True, verbose_name='Date de récolte')),
                ('kg_produced', models.IntegerField(blank=True, default=0, verbose_name='Quantité récoltée (kg)')),
                ('total_selling_price', models.IntegerField(blank=True, default=0, verbose_name='Prix de vente total (€)')),
                ('executor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Garden',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nom du jardin')),
                ('details_available_for_research', models.BooleanField(default=True, verbose_name="J'accepte que les données de mon jardin soient accessibles pour la recherche universitaire")),
                ('activity_data_available_for_research', models.BooleanField(default=True, verbose_name="J'accepte que les données de mes récoltes soient accessibles pour la recherche universitaire")),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('garden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='planner.garden')),
            ],
        ),
        migrations.CreateModel(
            name='HistoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execution_date', models.DateField(verbose_name="Date d'exécution")),
                ('area_concerned', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planner.cultivatedarea', verbose_name='Culture concernée')),
                ('executor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.history')),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('baseoperation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='common.baseoperation')),
            ],
            bases=('common.baseoperation',),
        ),
        migrations.CreateModel(
            name='Variety',
            fields=[
                ('basevariety_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='common.basevariety')),
            ],
            bases=('common.basevariety',),
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('historyitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='planner.historyitem')),
                ('description', models.TextField(verbose_name='Description')),
            ],
            bases=('planner.historyitem',),
        ),
        migrations.CreateModel(
            name='Vegetable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Espèce')),
                ('variety', models.CharField(blank=True, default='', max_length=100, verbose_name='Variété')),
                ('extern_id', models.IntegerField(null=True)),
                ('garden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.garden')),
            ],
            options={
                'unique_together': {('name', 'variety', 'garden')},
            },
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('basespecies_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='common.basespecies')),
                ('garden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.garden')),
            ],
            bases=('common.basespecies',),
        ),
        migrations.CreateModel(
            name='PerformedOperation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.operation')),
            ],
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nom')),
                ('geometry', django.contrib.gis.db.models.fields.PolygonField(geography=True, srid=4326)),
                ('orientation_segment', models.IntegerField(default=0)),
                ('garden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.garden')),
            ],
        ),
        migrations.AddField(
            model_name='cultivatedarea',
            name='garden',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.garden'),
        ),
        migrations.AddField(
            model_name='cultivatedarea',
            name='surface',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.bed', verbose_name='Planche'),
        ),
        migrations.AddField(
            model_name='cultivatedarea',
            name='vegetable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planner.vegetable', verbose_name='Légume cultivé'),
        ),
        migrations.AddField(
            model_name='bed',
            name='garden',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.garden'),
        ),
        migrations.AddField(
            model_name='bed',
            name='parcel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='planner.parcel', verbose_name='Parcelle'),
        ),
        django_db_constraints.operations.AlterConstraints(
            name='Parcel',
            db_constraints={'geometery_one_ring': 'CHECK (ST_NRings(geometry::geometry) = 1)', 'no_concave_geometry': 'CHECK (ST_equals(ST_ConvexHull(ST_Boundary(geometry::geometry)), geometry::geometry))'},
        ),
    ]
