# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AllTable(models.Model):
    wormbase_id = models.TextField(db_column='Wormbase_ID')  # Field name made lowercase.
    status = models.TextField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    sequence_name = models.TextField(db_column='Sequence_Name', blank=True, null=True)  # Field name made lowercase.
    gene_name = models.TextField(db_column='Gene_Name', blank=True, null=True)  # Field name made lowercase.
    other_names = models.TextField(db_column='Other_Names', blank=True, null=True)  # Field name made lowercase.
    transcript = models.TextField(db_column='Transcript', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    count = models.IntegerField(db_column='Transcript_count', blank=True, null=True)
    id =  models.IntegerField(db_column='pk',primary_key=True)
    
    class Meta:
        managed = False
        db_table = 'all_table'
        
class Duplicate(models.Model):
    name = models.CharField(db_column='Name',max_length=255, primary_key=True)  # 对应数据库中的 VARCHAR(255)
    duplicate_count = models.IntegerField(db_column='Count')
    wormbase_ids = models.TextField(db_column='Wormbase_IDs')
    class Meta:
        db_table = 'duplicate'  # 指定数据库表名