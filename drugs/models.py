from django.db import models

# Create your models here.
# class ProductionUnit(models.Model):
#     """docstring for ProductionUnit"""
#     production_unit_name = models.CharField(max_length = 45)
#     address = models.CharField(max_length = 100)
#     province = models.CharField('', max_length = 10)
#     city = models.CharField('', max_length = 10)
#     coordinate = models.CharField('', max_length = 45)
#     unit_link_address = models.URLField(max_length = 200)
#     class Meta:
#     	db_table = 'production_units'
# class ProductionUnit(models.Model):
#     production_unit_name = models.CharField(unique=True, max_length=45)
#     address = models.CharField(max_length=100)
#     province = models.CharField(max_length=10, blank=True, null=True)
#     city = models.CharField(max_length=10, blank=True, null=True)
#     coordinate = models.TextField(blank=True, null=True)  # This field type is a guess.
#     unit_linkid = models.PositiveIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'production_units'
#         unique_together = (('id', 'production_unit_name'),)
class ProductionUnits(models.Model):
    production_unit_name = models.CharField(unique=True, max_length=45)
    address = models.CharField(max_length=100)
    province = models.CharField(max_length=45, blank=True, null=True)
    city = models.CharField(max_length=45, blank=True, null=True)
    coordinate = models.TextField(blank=True, null=True)  # This field type is a guess.
    unit_link_index = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'production_units'
        unique_together = (('id', 'production_unit_name'),)
# class DrugApproved(models.Model):
#     '''
#     drug model with fields according to db drugs_approved
#     '''    
#     drug_index = models.IntegerField(primary_key = True)   
#     drug_approval_num = models.CharField(max_length = 45) 
#     drug_name_zh = models.CharField(max_length = 45) 
#     drug_name_en = models.TextField() 
#     drug_trade_name = models.CharField(max_length = 45, blank = True, null = True)
#     drug_form = models.CharField(max_length = 45) 
#     drug_spec = models.CharField(max_length = 200) 
#     category = models.CharField('', max_length = 45)
#     approval_date = models.DateField() 
#     origin_approval_num = models.CharField('', max_length = 45)
#     drug_standard_code = models.TextField()
#     drug_code_remark = models.TextField()
#     #keep sense to mark quotes on model class name, to avoid error
#     production_unit = models.ForeignKey('ProductionUnit',  on_delete = models.CASCADE)
#     drug_link_index = models.CharField(max_length = 45) 
#     class Meta:
#     	db_table = 'drugs_approved'

# class DrugApproved(models.Model):
#     drug_index = models.AutoField(primary_key=True)
#     drug_approval_num = models.CharField(unique=True, max_length=45)
#     drug_name_zh = models.CharField(max_length=45)
#     drug_name_en = models.TextField()
#     drug_trade_name = models.CharField(max_length=45, blank=True, null=True)
#     drug_form = models.CharField(max_length=45)
#     drug_spec = models.CharField(max_length=200)
#     category = models.CharField(max_length=45, blank=True, null=True)
#     approval_date = models.DateField()
#     origin_approval_num = models.CharField(max_length=45, blank=True, null=True)
#     drug_standard_code = models.TextField(blank=True, null=True)
#     drug_code_remark = models.TextField(blank=True, null=True)
#     production_unit = models.ForeignKey('ProductionUnit', models.DO_NOTHING)
#     drug_link_index = models.CharField(max_length=45)

#     class Meta:
#         managed = False
#         db_table = 'drugs_approved'

class DrugsApproved(models.Model):
    drug_index = models.AutoField(primary_key=True)
    drug_approval_num = models.CharField(unique=True, max_length=45)
    drug_name_zh = models.CharField(max_length=45)
    drug_name_en = models.TextField()
    drug_trade_name = models.CharField(max_length=45, blank=True, null=True)
    drug_form = models.CharField(max_length=45)
    drug_spec = models.CharField(max_length=200)
    category = models.CharField(max_length=45, blank=True, null=True)
    approval_date = models.DateField()
    origin_approval_num = models.CharField(max_length=45, blank=True, null=True)
    drug_standard_code = models.TextField(blank=True, null=True)
    drug_code_remark = models.TextField(blank=True, null=True)
    production_unit = models.ForeignKey('ProductionUnits', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'drugs_approved'
        
class PharmUnits(models.Model):
    unit_index = models.CharField(max_length=45, blank=True, null=True)
    unit_orgcode = models.CharField(max_length=45)
    unit_catgorycode = models.CharField(max_length=20, blank=True, null=True)
    unit_province = models.CharField(max_length=15, blank=True, null=True)
    unit_name = models.CharField(max_length=45)
    unit_person_inlaw = models.CharField(max_length=45, blank=True, null=True)
    unit_person_incharge = models.CharField(max_length=45, blank=True, null=True)
    unit_person_inquality = models.CharField(max_length=45, blank=True, null=True)
    unit_address = models.CharField(max_length=300, blank=True, null=True)
    unit_production_address = models.TextField(blank=True, null=True)
    unit_production_range = models.TextField(blank=True, null=True)
    unit_approved_date = models.DateField(blank=True, null=True)
    unit_expired_date = models.DateField(blank=True, null=True)
    unit_approved_admin = models.CharField(max_length=45, blank=True, null=True)
    unit_approved_person = models.CharField(max_length=45, blank=True, null=True)
    unit_admin_agency = models.CharField(max_length=45, blank=True, null=True)
    unit_admin_persons = models.CharField(max_length=300, blank=True, null=True)
    unit_linkid = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'pharm_units'