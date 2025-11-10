# Generated migration

from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisJob',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('job_type', models.CharField(choices=[('nlp', 'NLP Analysis'), ('embeddings', 'Embeddings Generation'), ('sentiment', 'Sentiment Analysis'), ('comparison', 'Comparison Analysis'), ('bulk_import', 'Bulk Data Import')], max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('parameters', models.JSONField(blank=True, default=dict)),
                ('results', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('total_items', models.IntegerField(default=0)),
                ('processed_items', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BillTextAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analyzed_at', models.DateTimeField(auto_now=True)),
                ('raw_text', models.TextField(blank=True)),
                ('sentiment_score', models.FloatField(blank=True, null=True)),
                ('sentiment_label', models.CharField(blank=True, max_length=20)),
                ('extracted_topics', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('entities', models.JSONField(blank=True, default=dict)),
                ('embeddings', models.JSONField(blank=True, default=list)),
                ('summary', models.TextField(blank=True)),
                ('analysis_metadata', models.JSONField(blank=True, default=dict)),
                ('bill', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='text_analysis', to='data.bill')),
            ],
            options={
                'verbose_name_plural': 'Bill text analyses',
            },
        ),
        migrations.CreateModel(
            name='LegislatorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('total_votes', models.IntegerField(default=0)),
                ('yes_votes', models.IntegerField(default=0)),
                ('no_votes', models.IntegerField(default=0)),
                ('abstain_votes', models.IntegerField(default=0)),
                ('other_votes', models.IntegerField(default=0)),
                ('total_sponsored_bills', models.IntegerField(default=0)),
                ('primary_sponsored_bills', models.IntegerField(default=0)),
                ('co_sponsored_bills', models.IntegerField(default=0)),
                ('primary_topics', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None)),
                ('voting_alignment', models.JSONField(blank=True, default=dict)),
                ('social_media_sentiment', models.FloatField(blank=True, null=True)),
                ('social_media_topics', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None)),
                ('voting_social_discrepancy', models.FloatField(blank=True, null=True)),
                ('recent_votes_summary', models.JSONField(blank=True, default=dict)),
                ('recent_bills_summary', models.JSONField(blank=True, default=dict)),
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analysis_profile', to='data.person')),
            ],
        ),
        migrations.CreateModel(
            name='VoteAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analyzed_at', models.DateTimeField(auto_now=True)),
                ('party_line_score', models.FloatField(blank=True, null=True)),
                ('bipartisan_score', models.FloatField(blank=True, null=True)),
                ('related_topics', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None)),
                ('bill_sentiment', models.FloatField(blank=True, null=True)),
                ('analysis_metadata', models.JSONField(blank=True, default=dict)),
                ('vote_event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vote_analysis', to='data.voteevent')),
            ],
            options={
                'verbose_name_plural': 'Vote analyses',
            },
        ),
        migrations.CreateModel(
            name='DataIngestionLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('database_type', models.CharField(max_length=50)),
                ('database_host', models.CharField(max_length=255)),
                ('database_name', models.CharField(max_length=255)),
                ('jurisdictions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), blank=True, default=list, size=None)),
                ('total_bills', models.IntegerField(default=0)),
                ('total_votes', models.IntegerField(default=0)),
                ('total_people', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='running', max_length=20)),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='MicroStatement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('actor', models.CharField(help_text='Who is taking action (e.g., legislators, politicians)', max_length=500)),
                ('action', models.CharField(help_text='What action is being taken (verb phrase)', max_length=500)),
                ('target', models.CharField(help_text='Who is affected (e.g., voters, citizens, groups)', max_length=500)),
                ('statement_text', models.TextField(help_text='Complete extracted statement')),
                ('original_text', models.TextField(blank=True, help_text='Original text from bill')),
                ('statement_type', models.CharField(choices=[('action', 'Legislative Action'), ('position', 'Political Position'), ('impact', 'Impact Statement')], default='action', max_length=20)),
                ('sentiment', models.CharField(choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral'), ('mixed', 'Mixed')], default='neutral', max_length=20)),
                ('sentiment_score', models.FloatField(blank=True, help_text='Sentiment score from -1 (negative) to 1 (positive)', null=True)),
                ('session_year', models.IntegerField(blank=True, help_text='Legislative session year', null=True)),
                ('jurisdiction', models.CharField(blank=True, help_text='State/jurisdiction code', max_length=10)),
                ('district', models.CharField(blank=True, help_text='Legislative district', max_length=100)),
                ('party', models.CharField(blank=True, help_text='Political party', max_length=50)),
                ('entities', models.JSONField(blank=True, default=dict, help_text='Named entities (people, orgs, locations)')),
                ('confidence_score', models.FloatField(blank=True, help_text='Confidence in extraction quality', null=True)),
                ('extraction_method', models.CharField(blank=True, help_text='Method used for extraction', max_length=100)),
                ('extracted_at', models.DateTimeField(auto_now_add=True)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='micro_statements', to='data.bill')),
                ('bill_text_analysis', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='micro_statements', to='analysis.billtextanalysis')),
            ],
            options={
                'ordering': ['-extracted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='analysisjob',
            index=models.Index(fields=['status', 'created_at'], name='analysis_an_status_bdb1c7_idx'),
        ),
        migrations.AddIndex(
            model_name='analysisjob',
            index=models.Index(fields=['job_type', 'status'], name='analysis_an_job_typ_8c8f9a_idx'),
        ),
        migrations.AddIndex(
            model_name='billtextanalysis',
            index=models.Index(fields=['sentiment_score'], name='analysis_bi_sentime_7e8b1f_idx'),
        ),
        migrations.AddIndex(
            model_name='legislatorprofile',
            index=models.Index(fields=['updated_at'], name='analysis_le_updated_3a7b2c_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['bill'], name='analysis_mi_bill_id_4a7c8d_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['session_year'], name='analysis_mi_session_5b8e9f_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['jurisdiction'], name='analysis_mi_jurisdi_6c9f0a_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['district'], name='analysis_mi_distric_7d0a1b_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['party'], name='analysis_mi_party_i_8e1b2c_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['sentiment'], name='analysis_mi_sentime_9f2c3d_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['statement_type'], name='analysis_mi_stateme_0a3d4e_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['session_year', 'jurisdiction'], name='analysis_mi_session_1b4e5f_idx'),
        ),
        migrations.AddIndex(
            model_name='microstatement',
            index=models.Index(fields=['session_year', 'party'], name='analysis_mi_session_2c5f6a_idx'),
        ),
    ]
