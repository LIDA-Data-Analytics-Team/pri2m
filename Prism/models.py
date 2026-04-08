# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Tblproject(models.Model):
    pid = models.AutoField(db_column='pID', primary_key=True, editable=False)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    projectname = models.CharField(db_column='ProjectName', max_length=500, blank=True, null=True)  # Field name made lowercase.
    portfolionumber = models.CharField(db_column='PortfolioNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    stage = models.ForeignKey('Tlkstage', models.PROTECT, db_column='Stage', blank=True, null=True)  # Field name made lowercase.
    classification = models.ForeignKey('Tlkclassification', models.PROTECT, db_column='Classification', blank=True, null=True)  # Field name made lowercase.
    datrag = models.IntegerField(db_column='DATRAG', blank=True, null=True)  # Field name made lowercase.
    projectedstartdate = models.DateTimeField(db_column='ProjectedStartDate', blank=True, null=True)  # Field name made lowercase.
    projectedenddate = models.DateTimeField(db_column='ProjectedEndDate', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    pi = models.IntegerField(db_column='PI', blank=True, null=True)  # Field name made lowercase.
    leadapplicant = models.IntegerField(db_column='LeadApplicant', blank=True, null=True)  # Field name made lowercase.
    faculty = models.ForeignKey('Tlkfaculty', models.PROTECT, db_column='Faculty', blank=True, null=True)  # Field name made lowercase.
    lida = models.BooleanField(db_column='LIDA', blank=True, null=True)  # Field name made lowercase.
    internship = models.BooleanField(db_column='Internship', blank=True, null=True)  # Field name made lowercase.
    dspt = models.BooleanField(db_column='DSPT', blank=True, null=True)  # Field name made lowercase.
    iso27001 = models.BooleanField(db_column='ISO27001', blank=True, null=True)  # Field name made lowercase.
    laser = models.BooleanField(db_column='LASER', blank=True, null=True)  # Field name made lowercase.
    irc = models.BooleanField(db_column='IRC', blank=True, null=True)  # Field name made lowercase.
    seed = models.BooleanField(db_column='SEED', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.projectnumber

    class Meta:
        managed = False
        db_table = 'tblProject'


class Tblprojectcostings(models.Model):
    projectcostingsid = models.IntegerField(db_column='ProjectCostingsId', primary_key=True)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    costingtypeid = models.IntegerField(db_column='CostingTypeId', blank=True, null=True)  # Field name made lowercase.
    datecosted = models.DateTimeField(db_column='DateCosted', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.DateTimeField(db_column='FromDate', blank=True, null=True)  # Field name made lowercase.
    todate = models.DateTimeField(db_column='ToDate', blank=True, null=True)  # Field name made lowercase.
    duration = models.DecimalField(db_column='Duration', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    durationcomputed = models.DecimalField(db_column='DurationComputed', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    lasercompute = models.DecimalField(db_column='LaserCompute', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    itssupport = models.DecimalField(db_column='ItsSupport', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fixedinfra = models.DecimalField(db_column='FixedInfra', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=12, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectCostings'


class Tblprojectdatallocation(models.Model):
    projectdatallocationid = models.AutoField(db_column='ProjectDatAllocationId', primary_key=True, editable=False)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    fromdate = models.DateTimeField(db_column='FromDate', blank=True, null=True)  # Field name made lowercase.
    todate = models.DateTimeField(db_column='ToDate', blank=True, null=True)  # Field name made lowercase.
    duration = models.DecimalField(db_column='Duration', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    durationcomputed = models.DecimalField(db_column='DurationComputed', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    fte = models.DecimalField(db_column='FTE', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    account = models.CharField(db_column='Account', max_length=25, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectDatAllocation'


class Tblprojectdattime(models.Model):
    dtid = models.IntegerField(db_column='dtID', primary_key=True)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    dathours = models.DecimalField(db_column='DatHours', max_digits=3, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectDatTime'


class Tblprojectdocument(models.Model):
    pdid = models.AutoField(db_column='pdID', primary_key=True, editable=False)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    documenttype = models.ForeignKey('Tlkdocuments', models.PROTECT, db_column='DocumentType', blank=True, null=True)  # Field name made lowercase.
    versionnumber = models.DecimalField(db_column='VersionNumber', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    submitted = models.DateTimeField(db_column='Submitted', blank=True, null=True)  # Field name made lowercase.
    accepted = models.DateTimeField(db_column='Accepted', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectDocument'


class Tblprojectkristal(models.Model):
    projectkristalid = models.AutoField(db_column='ProjectKristalID', primary_key=True)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    kristalnumber = models.DecimalField(db_column='KristalNumber', max_digits=6, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectKristal'


class Tblprojectnotes(models.Model):
    pnid = models.AutoField(db_column='pnID', primary_key=True, editable=False)
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    pnote = models.TextField(db_column='pNote', blank=True, null=True)  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectNotes'


class Tblprojectplatforminfo(models.Model):
    projectplatforminfoid = models.AutoField(db_column='ProjectPlatformInfoID', primary_key=True)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    platforminfoid = models.ForeignKey('Tlkplatforminfo', models.PROTECT, db_column='PlatformInfoID', blank=True, null=True)  # Field name made lowercase.
    projectplatforminfo = models.CharField(db_column='ProjectPlatformInfo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    platforminfodescription = models.CharField(db_column='PlatformInfoDescription', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProjectPlatformInfo'


class Tbldsdpcohort(models.Model):
    dsdpcohortid = models.AutoField(db_column='DSDPCohortID', primary_key=True)  # Field name made lowercase.
    cohort = models.CharField(db_column='Cohort', max_length=25, blank=True, null=True)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDSDPCohort'


class Tbluser(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    usernumber = models.IntegerField(db_column='UserNumber', blank=True, null=True)  # Field name made lowercase.
    status = models.ForeignKey('Tlkuserstatus', models.PROTECT, db_column='Status', blank=True, null=True)  # Field name made lowercase.
    title = models.ForeignKey('Tlktitle', models.PROTECT, db_column='Title', blank=True, null=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=15, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=12, blank=True, null=True)  # Field name made lowercase.
    organisation = models.CharField(db_column='Organisation', max_length=255, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    priviledged = models.BooleanField(db_column='Priviledged', blank=True, null=True)  # Field name made lowercase.
    seedagreement = models.DateTimeField(db_column='SEEDAgreement', blank=True, null=True)  # Field name made lowercase.
    ircagreement = models.DateTimeField(db_column='IRCAgreement', blank=True, null=True)  # Field name made lowercase.
    laseragreement = models.DateTimeField(db_column='LASERAgreement', blank=True, null=True)  # Field name made lowercase.
    dataprotection = models.DateTimeField(db_column='DataProtection', blank=True, null=True)  # Field name made lowercase.
    informationsecurity = models.DateTimeField(db_column='InformationSecurity', blank=True, null=True)  # Field name made lowercase.
    iset = models.DateTimeField(db_column='ISET', blank=True, null=True)  # Field name made lowercase.
    isat = models.DateTimeField(db_column='ISAT', blank=True, null=True)  # Field name made lowercase.
    safe = models.DateTimeField(db_column='SAFE', blank=True, null=True)  # Field name made lowercase.
    tokenserial = models.BigIntegerField(db_column='TokenSerial', blank=True, null=True)  # Field name made lowercase.
    tokenissued = models.DateTimeField(db_column='TokenIssued', blank=True, null=True)  # Field name made lowercase.
    tokenreturned = models.DateTimeField(db_column='TokenReturned', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    @property
    def full_name(self):
        "Returns the user's full name."
        return f"{self.firstname} {self.lastname}"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    
    class Meta:
        managed = False
        db_table = 'tblUser'


class Tbluserproject(models.Model):
    userprojectid = models.AutoField(db_column='UserProjectId', primary_key=True, editable=False)
    usernumber = models.IntegerField(db_column='UserNumber', blank=True, null=True)
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'tblUserProject'


class Tblkristal(models.Model):
    kristalid = models.AutoField(db_column='KristalID', primary_key=True)
    kristalnumber = models.IntegerField(db_column='KristalNumber', blank=True, null=True)
    kristalref = models.DecimalField(db_column='KristalRef', max_digits=6, decimal_places=0, blank=True, null=True)
    kristalname = models.CharField(db_column='KristalName', max_length=500, blank=True, null=True)
    grantstageid = models.ForeignKey('tlkGrantStage', models.PROTECT, db_column='GrantStageID', blank=True, null=True)
    pi = models.IntegerField(db_column='PI', blank=True, null=True)
    location = models.ForeignKey('Tlklocation', models.PROTECT, db_column='Location', blank=True, null=True)
    faculty = models.ForeignKey('Tlkfaculty', models.PROTECT, db_column='Faculty', blank=True, null=True)
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)
    laser = models.BooleanField(db_column='LASER', blank=True, null=True)  # Field name made lowercase.
    dsdp = models.BooleanField(db_column='DSDP', blank=True, null=True)  # Field name made lowercase.
    ridm = models.BooleanField(db_column='RIDM', blank=True, null=True)  # Field name made lowercase.
    community = models.BooleanField(db_column='Community', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.kristalnumber

    class Meta:
        managed = False
        db_table = 'tblKristal'


class Tblkristalnotes(models.Model):
    knid = models.AutoField(db_column='knID', primary_key=True)  # Field name made lowercase.
    kristalnumber = models.IntegerField(db_column='KristalNumber', blank=True, null=True)  # Field name made lowercase.
    kristalnote = models.TextField(db_column='KristalNote', blank=True, null=True)  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblKristalNotes'


class Tlkclassification(models.Model):
    classificationid = models.IntegerField(db_column='classificationID', primary_key=True)  # Field name made lowercase.
    classificationdescription = models.CharField(db_column='classificationDescription', max_length=25, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.classificationdescription

    class Meta:
        managed = False
        db_table = 'tlkClassification'


class Tlkcostingtype(models.Model):
    costingtypeid = models.IntegerField(db_column='CostingTypeId', primary_key=True)  # Field name made lowercase.
    costingtypedescription = models.CharField(db_column='CostingTypeDescription', max_length=25, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=12, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.costingtypedescription

    class Meta:
        managed = False
        db_table = 'tlkCostingType'


class Tlkdocuments(models.Model):
    documentid = models.IntegerField(db_column='DocumentID', primary_key=True)  # Field name made lowercase.
    documentdescription = models.CharField(db_column='DocumentDescription', max_length=50, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.documentdescription
    
    class Meta:
        managed = False
        db_table = 'tlkDocuments'


class Tlkfaculty(models.Model):
    facultyid = models.IntegerField(db_column='facultyID', primary_key=True)  # Field name made lowercase.
    facultydescription = models.CharField(db_column='facultyDescription', max_length=100, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.facultydescription

    class Meta:
        managed = False
        db_table = 'tlkFaculty'


class Tlkplatforminfo(models.Model):
    platforminfoid = models.IntegerField(db_column='PlatformInfoID', primary_key=True)  # Field name made lowercase.
    platforminfodescription = models.CharField(db_column='PlatformInfoDescription', max_length=50, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.platforminfodescription

    class Meta:
        managed = False
        db_table = 'tlkPlatformInfo'


class Tlkstage(models.Model):
    stageid = models.IntegerField(db_column='StageID', primary_key=True)  # Field name made lowercase.
    pstagedescription = models.CharField(db_column='pStageDescription', max_length=25, blank=True, null=True)  # Field name made lowercase.
    stagenumber = models.DecimalField(db_column='StageNumber', max_digits=3, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.pstagedescription

    class Meta:
        managed = False
        db_table = 'tlkStage'


class Tlktitle(models.Model):
    titleid = models.IntegerField(db_column='TitleID', primary_key=True)  # Field name made lowercase.
    titledescription = models.CharField(db_column='TitleDescription', max_length=25, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.titledescription

    class Meta:
        managed = False
        db_table = 'tlkTitle'


class Tlkuserstatus(models.Model):
    statusid = models.IntegerField(db_column='StatusID', primary_key=True)  # Field name made lowercase.
    statusdescription = models.CharField(db_column='StatusDescription', max_length=25, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.statusdescription

    class Meta:
        managed = False
        db_table = 'tlkUserStatus'


class Tlklocation(models.Model):
    locationid = models.AutoField(db_column='locationID', primary_key=True)
    locationdescription = models.CharField(db_column='locationDescription', max_length=100, blank=True, null=True)
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)

    def __str__(self):
        return self.locationdescription

    class Meta:
        managed = False
        db_table = 'tlkLocation'


class tlkGrantStage(models.Model):
    grantstageid = models.AutoField(db_column='GrantStageID', primary_key=True)
    stagenumber = models.DecimalField(db_column='StageNumber', max_digits=3, decimal_places=1, blank=True, null=True)
    grantstagedescription = models.CharField(db_column='GrantStageDescription', max_length=25, blank=True, null=True)
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)

    def __str__(self):
        return self.grantstagedescription

    class Meta:
        managed = False
        db_table = 'tlkGrantStage'


class Tblusernotes(models.Model):
    unid = models.AutoField(db_column='unID', primary_key=True, editable=False)
    usernumber = models.IntegerField(db_column='UserNumber', blank=True, null=True)
    unote = models.TextField(db_column='uNote', blank=True, null=True)
    created = models.DateTimeField(db_column='Created', blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblUserNotes'


class Tbldsadataowners(models.Model):
    doid = models.AutoField(db_column='doID', primary_key=True)  # Field name made lowercase.
    dataownername = models.CharField(db_column='DataOwnerName', unique=True, max_length=100)  # Field name made lowercase.
    rebrandof = models.ForeignKey('self', models.PROTECT, db_column='RebrandOf', blank=True, null=True)  # Field name made lowercase.
    dataowneremail = models.CharField(db_column='DataOwnerEmail', max_length=50, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.dataownername

    class Meta:
        managed = False
        db_table = 'tblDsaDataOwners'


class Tbldsanotes(models.Model):
    dnid = models.AutoField(db_column='dnID', primary_key=True, editable=False)  # Field name made lowercase.
    dsa = models.IntegerField(db_column='Dsa')  # Field name made lowercase.
    note = models.TextField(db_column='Note', blank=True, null=True)  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDsaNotes'


class Tbldsas(models.Model):
    dsaid = models.AutoField(db_column='DsaID', primary_key=True)  # Field name made lowercase.
    documentid = models.IntegerField(db_column='DocumentID')  # Field name made lowercase.
    dataowner = models.ForeignKey(Tbldsadataowners, models.PROTECT, db_column='DataOwner')  # Field name made lowercase.
    amendmentof = models.ForeignKey('self', models.PROTECT, db_column='AmendmentOf', blank=True, null=True)  # Field name made lowercase.
    dsaname = models.CharField(db_column='DsaName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dsafileloc = models.CharField(db_column='DsaFileLoc', max_length=200, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    expirydate = models.DateTimeField(db_column='ExpiryDate', blank=True, null=True)  # Field name made lowercase.
    datadestructiondate = models.DateTimeField(db_column='DataDestructionDate', blank=True, null=True)  # Field name made lowercase.
    agreementowneremail = models.CharField(db_column='AgreementOwnerEmail', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dspt = models.BooleanField(db_column='DSPT', blank=True, null=True)  # Field name made lowercase.
    iso27001 = models.BooleanField(db_column='ISO27001', blank=True, null=True)  # Field name made lowercase.
    requiresencryption = models.BooleanField(db_column='RequiresEncryption', blank=True, null=True)  # Field name made lowercase.
    noremoteaccess = models.BooleanField(db_column='NoRemoteAccess', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    deprecated = models.BooleanField(db_column='Deprecated') #, null=False, db_default=False)  # Field name made lowercase.

    def __str__(self):
        return self.dsaname

    class Meta:
        managed = False
        db_table = 'tblDsas'


class Tbldsasprojects(models.Model):
    dpid = models.AutoField(db_column='dpID', primary_key=True)  # Field name made lowercase.
    documentid = models.IntegerField(db_column='DocumentID')  # Field name made lowercase.
    project = models.CharField(db_column='Project', max_length=5, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDsasProjects'


class Tbltransferfile(models.Model):
    fileid = models.AutoField(db_column='FileID', primary_key=True)  # Field name made lowercase.
    requestid = models.ForeignKey('Tbltransferrequest', models.PROTECT, db_column='RequestID')  # Field name made lowercase.
    filename = models.CharField(db_column='FileName', max_length=300)  # Field name made lowercase.
    trefilepath = models.CharField(db_column='TreFilePath', max_length=200, blank=True, null=True)  # Field name made lowercase.
    datarepofilepath = models.CharField(db_column='DataRepoFilePath', max_length=200, blank=True, null=True)  # Field name made lowercase.
    transferaccepted = models.BooleanField(db_column='TransferAccepted', blank=True, null=True)  # Field name made lowercase.
    rejectionnotes = models.TextField(db_column='RejectionNotes', blank=True, null=True)  # Field name made lowercase.
    assetid = models.ForeignKey('Tbltransferfileasset', models.PROTECT, db_column='AssetID', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblTransferFile'


class Tbltransferfileasset(models.Model):
    assetid = models.AutoField(db_column='AssetID', primary_key=True)  # Field name made lowercase.
    assetname = models.CharField(db_column='AssetName', max_length=500, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.assetname or ""

    class Meta:
        managed = False
        db_table = 'tblTransferFileAsset'


class Tbltransferrequest(models.Model):
    requestid = models.AutoField(db_column='RequestID', primary_key=True)  # Field name made lowercase.
    projectnumber = models.CharField(db_column='ProjectNumber', max_length=5, blank=True, null=True)  # Field name made lowercase.
    # vrenumber = models.CharField(db_column='VreNumber', max_length=15, blank=True, null=True)  # Field name made lowercase.
    requesttype = models.ForeignKey('Tlktransferrequesttypes', models.PROTECT, db_column='RequestType')  # Field name made lowercase.
    requestedby = models.IntegerField(db_column='RequestedBy', blank=True, null=True)  # Field name made lowercase.
    requesternotes = models.TextField(db_column='RequesterNotes', blank=True, null=True)  # Field name made lowercase.
    reviewedby = models.IntegerField(db_column='ReviewedBy', blank=True, null=True)  # Field name made lowercase.
    reviewdate = models.DateTimeField(db_column='ReviewDate', blank=True, null=True)  # Field name made lowercase.
    reviewnotes = models.TextField(db_column='ReviewNotes', blank=True, null=True)  # Field name made lowercase.
    transfermethod = models.ForeignKey('Tlkfiletransfermethods', models.PROTECT, db_column='TransferMethod', blank=True, null=True)  # Field name made lowercase.
    transferfrom = models.CharField(db_column='TransferFrom', max_length=250, blank=True, null=True)  # Field name made lowercase.
    transferto = models.CharField(db_column='TransferTo', max_length=250, blank=True, null=True)  # Field name made lowercase.
    dsareviewed = models.IntegerField(db_column='DsaReviewed', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblTransferRequest'


class Tlkfiletransfermethods(models.Model):
    methodid = models.AutoField(db_column='MethodID', primary_key=True)  # Field name made lowercase.
    methodlabel = models.CharField(db_column='MethodLabel', max_length=30, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.methodlabel

    class Meta:
        managed = False
        db_table = 'tlkFileTransferMethods'


class Tlktransferrequesttypes(models.Model):
    requesttypeid = models.AutoField(db_column='RequestTypeID', primary_key=True)  # Field name made lowercase.
    requesttypelabel = models.CharField(db_column='RequestTypeLabel', max_length=25, blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateTimeField(db_column='ValidFrom', blank=True, null=True)  # Field name made lowercase.
    validto = models.DateTimeField(db_column='ValidTo', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.requesttypelabel

    class Meta:
        managed = False
        db_table = 'tlkTransferRequestTypes'

    