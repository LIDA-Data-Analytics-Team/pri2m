from django import forms
from django.db.models import ForeignKey
from .models import Tlkstage, Tblproject, Tlkclassification, Tlkfaculty, Tbluser, Tblprojectnotes, Tblprojectdocument \
    , Tlkdocuments, Tblprojectplatforminfo, Tlkplatforminfo, Tblprojectdatallocation, Tlkuserstatus, Tbluserproject \
    , Tblusernotes, tlkGrantStage, Tlklocation, Tblkristal, Tblprojectkristal, Tblkristalnotes, Tbldsas, Tbldsadataowners \
    , Tbldsanotes, Tbldsasprojects, Tbltransferrequest, Tlktransferrequesttypes, Tlkfiletransfermethods, Tbltransferfileasset \
    , Tbltransferfile, Tbldsdpcohort
from django.utils import timezone

class DateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)

def ForiegnKeysAreValid(form, **kwargs):
    # Loop through each field in form and if it's a ForeignKey check if the current value is valid.
    # If not valid (ie ValidTo is not null) then add it to the queryset so it still displays on page
    for name, field in form.fields.items():
        if isinstance(form.Meta.model._meta.get_field(name), ForeignKey):
            qs = form.fields[name].queryset
            if 'initial' in kwargs:
                if not qs.filter(pk=kwargs['initial'][name]):
                    form.fields[name].queryset = (qs | qs.model.objects.filter(pk=kwargs['initial'][name]))
            elif 'data' in kwargs:
                if not qs.filter(pk=kwargs['data'][name]):
                    form.fields[name].queryset = (qs | qs.model.objects.filter(pk=kwargs['data'][name]))

class ProjectSearchForm(forms.Form):
    stage_id= forms.ModelChoiceField(label="Stage", queryset=Tlkstage.objects.filter(validto__isnull=True).order_by("stagenumber"), required=False)
    classification_id= forms.ModelChoiceField(label="Classification", queryset=Tlkclassification.objects.filter(validto__isnull=True).order_by("classificationdescription"), required=False)
    user = forms.ModelChoiceField(label="PI or Lead Applicant", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber", required=False)
    faculty_id= forms.ModelChoiceField(label="Faculty", queryset=Tlkfaculty.objects.filter(validto__isnull=True).order_by("facultydescription"), required=False)
    laser= forms.BooleanField(label="LASER", required=False)
    internship= forms.BooleanField(label="DSDP", required=False)
    cohort = forms.ModelChoiceField(label="DSDP Cohort", queryset=Tbldsdpcohort.objects.values_list("cohort", flat=True).distinct().order_by("cohort"), required=False)
        
    class Meta:
        model = Tblproject

class ProjectForm(forms.Form):
    pid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber= forms.CharField(label="Project Number", disabled=True, max_length=5, required=False)
    projectname= forms.CharField(label="Project Name", max_length=500)
    portfolionumber = forms.CharField(label="Portfolio Number", widget = forms.HiddenInput(), required=False, max_length=255)
    stage_id= forms.ModelChoiceField(label="Stage", queryset=Tlkstage.objects.filter(validto__isnull=True).order_by("stagenumber"))
    classification_id= forms.ModelChoiceField(label="Classification", queryset=Tlkclassification.objects.filter(validto__isnull=True).order_by("classificationdescription"))
    datrag = forms.IntegerField(label="DAT RAG", widget = forms.HiddenInput(), required=False)
    projectedstartdate= forms.DateTimeField(label="Projected Start Date", widget = DateInput())
    projectedenddate= forms.DateTimeField(label="Projected End Date", widget = DateInput())
    startdate= forms.DateTimeField(label="Start Date", widget = DateInput(), required=False)
    enddate= forms.DateTimeField(label="End Date", widget = DateInput(), required=False)
    pi = forms.ModelChoiceField(label="PI", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber")
    leadapplicant= forms.ModelChoiceField(label="Lead Applicant", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber")
    faculty_id= forms.ModelChoiceField(label="Faculty", queryset=Tlkfaculty.objects.filter(validto__isnull=True).order_by("facultydescription"))
    lida= forms.BooleanField(label="LIDA", required=False, initial=True)
    internship= forms.BooleanField(label="DSDP", required=False)
    dspt= forms.BooleanField(label="NHS DSPT", required=False)
    iso27001= forms.BooleanField(label="ISO27001", required=False)
    laser= forms.BooleanField(label="LASER", required=False)
    irc= forms.BooleanField(label="IRC", required=False)
    seed= forms.BooleanField(label="SEED", required=False)
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)
    
    def clean(self):
        cleaned_data = super().clean()
        startdate = cleaned_data.get("startdate")
        enddate = cleaned_data.get("enddate")
        projectedstartdate = cleaned_data.get("projectedstartdate")
        projectedenddate = cleaned_data.get("projectedenddate")
        
        # Do project start and end dates sequence correctly?
        if projectedstartdate is not None and projectedenddate is not None:
            if (projectedstartdate - projectedenddate).days >= 0:
                self.add_error(None, "Projected Start Date cannot be later than Projected End Date.")
        if startdate is not None and enddate is not None:
            if (startdate - enddate).days >= 0:
                self.add_error(None, "Start Date cannot be later than End Date.")

        if "stage_id" in cleaned_data:
            stage = cleaned_data["stage_id"].pstagedescription
            # If Stage is Active/Store/Destroy do Start Date and End Date exist?
            if (stage == "Active" or stage == "Store") and startdate is None:
                self.add_error(None, "Project cannot have started without a Start Date")
            if (stage == "Destroy") and (enddate is None or startdate is None):
                self.add_error(None, "Project cannot End without both a Start and End Date")
            # If adding Start/End Dates does the Stage align?
            if startdate and (stage == "Proposal" or stage == "Pre-grant" or stage == "Pre-Approval" or stage == "Setup"):
                self.add_error(None, "Project cannot have a Start Date while in a pre-Active Stage")
            if enddate and not (stage == "Destroy" or stage == "Discontinued"):
                self.add_error(None, "Project cannot have a End Date without being in a Destroy or Discontinued Stage")

        return self.cleaned_data
        

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        # When creating the form with initial data, we still want to validate the form. 
        # This `__init__` override will populate a temporary form (temp) with `data=initial` (as if POST) to trigger validation and 
        # therefore the `clean()` function above.
        # Any errors are copied to the original form and displayed with the data from the database.
        if self.initial: 
            ForiegnKeysAreValid(self, **kwargs)
            temp = type(self)(data=self.initial) 
            if not temp.is_valid(): 
                self._errors = temp.errors

    class Meta:
        model = Tblproject

class ProjectNotesForm(forms.Form):
    pnid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber = forms.CharField(widget = forms.HiddenInput(), label="Project Number", disabled=True, max_length=5, required=False)
    pnote = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "placeholder": "New note..."}), label="Project Note", max_length=500)
    created = forms.DateTimeField(widget = forms.HiddenInput(), label="Created", disabled=True, required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), label="Created By", disabled=True, max_length=50, required=False)

    class Meta:
        model = Tblprojectnotes

class ProjectDocumentsForm(forms.Form):
    pdid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber = forms.CharField(widget = forms.HiddenInput(), label="Project Number", disabled=True, max_length=5, required=False)
    documenttype = forms.ModelChoiceField(label="Document Type", queryset=Tlkdocuments.objects.filter(validto__isnull=True).order_by("documentid"))
    versionnumber = forms.DecimalField(label="Version Number", widget= forms.HiddenInput() , required=False) #forms.NumberInput(attrs={'step': 1}))
    submitted = forms.DateTimeField(label="Submitted Date", widget = DateInput(), initial=timezone.now())
    accepted = forms.DateTimeField(label="Accepted Date", widget = DateInput(), required=False)
    validfrom = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    validto = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    class Meta:
        model=Tblprojectdocument

class ProjectPlatformInfoForm(forms.Form):
    projectplatforminfoid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber = forms.CharField(widget = forms.HiddenInput(), label="Project Number", disabled=True, max_length=5, required=False)
    platforminfoid = forms.ModelChoiceField(label="Platform Item", queryset=Tlkplatforminfo.objects.filter(validto__isnull=True).order_by("platforminfoid"))
    projectplatforminfo = forms.CharField(label="Platform Info", widget=forms.Textarea(attrs={"rows":1, "placeholder": "Description..."}), max_length=255)
    validfrom = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    validto = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)
    platforminfodescription = forms.CharField(label="Platform Info Description", max_length=25, required=False)

    class Meta:
        model=Tblprojectplatforminfo

class ProjectDatAllocationForm(forms.Form):
    projectdatallocationid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber = forms.CharField(widget = forms.HiddenInput(), label="Project Number", disabled=True, max_length=5, required=False)
    fromdate = forms.DateTimeField(label="From Date", widget = DateInput(attrs={"placeholder": "From Date..."}))
    todate = forms.DateTimeField(label="To Date", widget = DateInput())
    duration = forms.DecimalField(label="Duration", widget= forms.HiddenInput() , required=False)
    durationcomputed = forms.DecimalField(label="Duration Computed", widget= forms.HiddenInput() , required=False)
    fte = forms.DecimalField(label="FTE", widget=forms.NumberInput(attrs={"placeholder": "FTE (min 2.5%)"}), required=True, min_value=2.5)
    account = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "UoL account to charge"}), label="Account code", max_length=25, required=False)
    validfrom = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    validto = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        fromdate = cleaned_data.get("fromdate")
        todate = cleaned_data.get("todate")

        if (fromdate - todate).days >= 0:
            self.add_error(None, "To Date cannot be earlier than From Date.")
        return self.cleaned_data

    class Meta:
        model=Tblprojectdatallocation

class DSDPCohortForm(forms.Form):
    dsdpcohortid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    cohort = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Cohort identifier"}), label="DSDP Cohort", max_length=25, required=False)
    projectnumber = forms.CharField(widget = forms.HiddenInput(), label="Project Number", disabled=True, max_length=5, required=False)

    class Meta:
        model=Tbldsdpcohort

class KristalForm(forms.Form):
    kristalid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    kristalnumber = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    kristalref = forms.DecimalField(label="Kristal Ref", widget=forms.NumberInput(attrs={"placeholder": "New Kristal Ref..."}), min_value=100000, max_value=999999)
    kristalname = forms.CharField(label="Kristal Name", max_length=500, required=False)
    grantstageid_id = forms.ModelChoiceField(label="Grant Stage", queryset=tlkGrantStage.objects.filter(validto__isnull=True).order_by("stagenumber"), required=False)
    pi = forms.ModelChoiceField(label="PI", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber", required=False)
    location_id = forms.ModelChoiceField(label="Location", queryset=Tlklocation.objects.filter(validto__isnull=True).order_by("locationdescription"), required=False)
    faculty_id = forms.ModelChoiceField(label="Faculty", queryset=Tlkfaculty.objects.filter(validto__isnull=True).order_by("facultydescription"), required=False)
    validfrom = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    validto = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)
    laser = forms.BooleanField(label="LASER", required=False)
    dsdp = forms.BooleanField(label="DSDP", required=False)
    ridm = forms.BooleanField(label="RIDM", required=False)
    community = forms.BooleanField(label="Community", required=False)

    def clean(self):
        cleaned_data = super().clean()
        kristalref = cleaned_data.get("kristalref")

        if Tblkristal.objects.filter(validto__isnull=True, kristalref=kristalref).exists():
            self.add_error(None, "That KristalRef already exists in Prism")

        return self.cleaned_data

    class Meta:
        model=Tblkristal

class ProjectKristalForm(forms.Form):
    projectkristalid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber = forms.ModelChoiceField(label="Project Number", empty_label="Select project", queryset=Tblproject.objects.filter(validto__isnull=True).order_by("projectnumber"), to_field_name="projectnumber")
    kristalnumber = forms.IntegerField(widget = forms.HiddenInput())
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        projectnumber = cleaned_data.get('projectnumber')
        kristalnumber = cleaned_data.get('kristalnumber')

        if Tblprojectkristal.objects.filter(validto__isnull=True, kristalnumber=kristalnumber, projectnumber=projectnumber).exists():
            self.add_error(None, "Grant is already on Project")

        return self.cleaned_data

    class Meta:
        model = Tblprojectkristal

class UserSearchForm(forms.Form):
    status_id = forms.ModelChoiceField(label="Status", queryset=Tlkuserstatus.objects.filter(validto__isnull=True).order_by("statusid"), required=False )
    username = forms.CharField(label="User Name", max_length=12, required=False)
    email = forms.CharField(label="Email", max_length=255, required=False) 
    organisation = forms.CharField(label="Organisation", max_length=255, required=False)

    class Meta:
        model = Tbluser

class UserForm(forms.Form):
    userid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    usernumber = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    status_id = forms.ModelChoiceField(label="Status", queryset=Tlkuserstatus.objects.filter(validto__isnull=True).order_by("statusid") )
    # title_id = forms.ModelChoiceField(label='Title', queryset=Tlktitle.objects.filter(validto__isnull=True).order_by("titledescription"), required=False )
    firstname = forms.CharField(label="First Name", max_length=50)
    lastname = forms.CharField(label="Last Name", max_length=50)
    email = forms.CharField(label="Email", max_length=255, required=False) 
    phone = forms.CharField(label="Phone", max_length=15, required=False)
    username = forms.CharField(label="User Name", max_length=12, required=False)
    organisation = forms.CharField(label="Organisation", max_length=255)
    startdate = forms.DateTimeField(label="Start Date", widget = DateInput(), required=False)
    enddate = forms.DateTimeField(label="End Date", widget = DateInput(), required=False)
    priviledged = forms.BooleanField(widget = forms.HiddenInput(), label="Priviledged", required=False)
    # seedagreement = forms.BooleanField(label="SEED Agreement", required=False)
    # ircagreement = forms.BooleanField(label="IRC Agreement", required=False)
    laseragreement = forms.DateTimeField(label="LASER Agreement", widget = DateInput(), required=False)
    dataprotection = forms.DateTimeField(label="Data Protection", widget = DateInput(), required=False)
    informationsecurity = forms.DateTimeField(label="Information Security", widget = DateInput(), required=False)
    # iset = forms.DateTimeField(label="ISET", widget = DateInput(), required=False)
    # isat = forms.DateTimeField(label="ISAT", widget = DateInput(), required=False)
    safe = forms.DateTimeField(label="Safe Researcher", widget = DateInput(), required=False)
    # tokenserial = forms.IntegerField(label="Token Serial", widget = forms.HiddenInput(), required=False)
    # tokenissued = forms.DateTimeField(label="Token Issued", widget = DateInput(), required=False)
    # tokenreturned = forms.DateTimeField(label="Token Returned", widget = DateInput(), required=False)
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        startdate = cleaned_data.get("startdate")
        enddate = cleaned_data.get("enddate")
        laseragreement = cleaned_data.get("laseragreement")
        dataprotection = cleaned_data.get("dataprotection")
        informationsecurity = cleaned_data.get("informationsecurity")
        safe = cleaned_data.get("safe")
        
        # Do user start and end dates sequence correctly?
        if startdate is not None and enddate is not None:
            if (startdate - enddate).days >= 0:
                self.add_error(None, "Start Date cannot be later than End Date.")

        if "status_id" in cleaned_data:
            status = cleaned_data["status_id"].statusdescription
            # If Status is Enabled/Disabled do Start Date and End Date exist?
            if status == "Enabled" and startdate is None:
                self.add_error(None, "User cannot be 'Enabled' without a Start Date")
            if status == "Disabled" and (enddate is None or startdate is None):
                self.add_error(None, "User cannot be 'Disabled' without both a Start and End Date")
            # If adding Start/End Dates does the Status align?
            if startdate and status == "Pending":
                self.add_error(None, "User cannot have a Start Date while 'Pending'")
            if enddate and not status == "Disabled":
                self.add_error(None, "User cannot have a End Date while not 'Disabled'")
            # If Status is Enabled do we have correct UserDocs?
            if status == "Enabled" and safe is None:
                if laseragreement is None or dataprotection is None or informationsecurity is None:
                    self.add_error(None, "User cannot be 'Enabled' without correct User Docs")
            elif status == "Enabled" and safe is not None:
                if laseragreement is None:
                    self.add_error(None, "User cannot be 'Enabled' without correct User Docs")

        return self.cleaned_data

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        # When creating the form with initial data, we still want to validate the form. 
        # This `__init__` override will populate a temporary form (temp) with `data=initial` (as if POST) to trigger validation and 
        # therefore the `clean()` function above.
        # Any errors are copied to the original form and displayed with the data from the database.
        if self.initial: 
            ForiegnKeysAreValid(self, **kwargs)
            temp = type(self)(data=self.initial) 
            if not temp.is_valid(): 
                self._errors = temp.errors

    class Meta:
        model = Tbluser

class UserProjectForm(forms.Form):
    userprojectid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    usernumber = forms.ModelChoiceField(label="Member", empty_label="Select user", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber")
    projectnumber = forms.ModelChoiceField(label="Project Number", empty_label="Select project", queryset=Tblproject.objects.filter(validto__isnull=True).order_by("projectnumber"), to_field_name="projectnumber")
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        projectnumber = cleaned_data.get('projectnumber').projectnumber
        usernumber = cleaned_data.get('usernumber').usernumber

        if Tbluserproject.objects.filter(validto__isnull=True, usernumber=usernumber, projectnumber=projectnumber).exists():
            self.add_error(None, "User is already on Project")

        return self.cleaned_data

    class Meta:
        model = Tbluserproject

class UserNotesForm(forms.Form):
    unid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    usernumber = forms.CharField(widget = forms.HiddenInput(), label="User Number", disabled=True, max_length=5, required=False)
    unote = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "placeholder": "New note..."}), label="User Note", max_length=500)
    created = forms.DateTimeField(widget = forms.HiddenInput(), label="Created", disabled=True, required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), label="Created By", disabled=True, max_length=50, required=False)

    class Meta:
        model = Tblusernotes

class GrantSearchForm(forms.Form):
    grantstageid_id = forms.ModelChoiceField(label="Stage", queryset=tlkGrantStage.objects.filter(validto__isnull=True).order_by("stagenumber"), required=False )
    faculty_id = forms.ModelChoiceField(label="Faculty", queryset=Tlkfaculty.objects.filter(validto__isnull=True).order_by("facultydescription"), required=False )
    location_id = forms.ModelChoiceField(label="Location", queryset=Tlklocation.objects.filter(validto__isnull=True).order_by("locationdescription"), required=False )
    laser= forms.BooleanField(label="LASER", required=False)
    dsdp= forms.BooleanField(label="DSDP", required=False)
    ridm= forms.BooleanField(label="RIDM", required=False)
    community= forms.BooleanField(label="Community", required=False)

    class Meta:
        model = Tblkristal

class GrantNotesForm(forms.Form):
    knid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    kristalnumber = forms.CharField(widget = forms.HiddenInput(), label="Kristal Number", disabled=True, max_length=5, required=False)
    kristalnote = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "placeholder": "New note..."}), label="User Note", max_length=500)
    created = forms.DateTimeField(widget = forms.HiddenInput(), label="Created", disabled=True, required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), label="Created By", disabled=True, max_length=50, required=False)

    class Meta:
        model = Tblkristalnotes

class DsaForm (forms.Form):
    dsaid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    documentid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    dataowner_id = forms.ModelChoiceField(label="Data Owner", queryset=Tbldsadataowners.objects.order_by("dataownername"))
    # amendmentof_id = forms.ModelChoiceField(label="Amendment Of", queryset=Tbldsas.objects.filter(validto__isnull=True).order_by("dsaname"), required=False)
    dsaname = forms.CharField(label="DSA File Name", max_length=100)
    dsafileloc = forms.CharField(label="DSA File Location", max_length=200)
    startdate = forms.DateTimeField(label="Start Date", widget = DateInput())
    expirydate = forms.DateTimeField(label="Expiry Date", widget = DateInput(), required=False)
    datadestructiondate = forms.DateTimeField(label="Data Destruction Date", widget = DateInput(), required=False)
    agreementowneremail = forms.CharField(label="Agreement Owner Email", max_length=50, required=False) 
    dspt = forms.BooleanField(label="NHS DSPT", required=False)
    iso27001 = forms.BooleanField(label="ISO27001", required=False)
    requiresencryption = forms.BooleanField(label="Requires Encryption", required=False)
    noremoteaccess = forms.BooleanField(label="No Remote Access", required=False)
    validfrom = forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto = forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    deprecated = forms.BooleanField(label="Deprecated", required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        startdate = cleaned_data.get("startdate")
        expirydate = cleaned_data.get("expirydate")
        datadestructiondate = cleaned_data.get("datadestructiondate")
        
        # Do DSA start and end dates sequence correctly?
        if startdate is not None and expirydate is not None:
            if (startdate - expirydate).days >= 0:
                self.add_error(None, "Start Date cannot be later than Expiry Date.")
        if startdate is not None and datadestructiondate is not None:
            if (startdate - datadestructiondate).days >= 0:
                self.add_error(None, "Start Date cannot be later than Data Destruction Date.")

        return self.cleaned_data
        

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        # When creating the form with initial data, we still want to validate the form. 
        # This `__init__` override will populate a temporary form (temp) with `data=initial` (as if POST) to trigger validation and 
        # therefore the `clean()` function above.
        # Any errors are copied to the original form and displayed with the data from the database.
        if self.initial: 
            ForiegnKeysAreValid(self, **kwargs)
            temp = type(self)(data=self.initial) 
            if not temp.is_valid(): 
                self._errors = temp.errors

    class Meta:
        model = Tbldsas

class DsaNotesForm(forms.Form):
    dnid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    dsa = forms.CharField(widget = forms.HiddenInput(), label="DSA ID", disabled=True, max_length=5, required=False)
    note = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "placeholder": "New note..."}), label="DSA Note", max_length=500)
    created = forms.DateTimeField(widget = forms.HiddenInput(), label="Created", disabled=True, required=False)
    createdby = forms.CharField(widget = forms.HiddenInput(), label="Created By", disabled=True, max_length=50, required=False)

    class Meta:
        model = Tbldsanotes

class ProjectDsaForm(forms.Form):
    dpid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    documentid = forms.IntegerField(widget = forms.HiddenInput()) 
    project = forms.ModelChoiceField(label="Project Number", empty_label="Select project", queryset=Tblproject.objects.filter(validto__isnull=True).order_by("projectnumber"), to_field_name="projectnumber")
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        documentid = cleaned_data.get('documentid')
        project = cleaned_data.get('project')

        if Tbldsasprojects.objects.filter(validto__isnull=True, documentid=documentid, project=project).exists():
            self.add_error(None, "DSA is already on Project")

        return self.cleaned_data

    class Meta:
        model = Tbldsasprojects

class DsaSearchForm(forms.Form):
    dataowner_id = forms.ModelChoiceField(label="Data Owner", queryset=Tbldsadataowners.objects.order_by("dataownername"), required=False)
    project = forms.ModelChoiceField(label="Project Number", queryset=Tblproject.objects.filter(validto__isnull=True).order_by("projectnumber"), to_field_name="projectnumber", required=False)
    dspt = forms.BooleanField(label="NHS DSPT", required=False)
    iso27001 = forms.BooleanField(label="ISO27001", required=False)
    requiresencryption = forms.BooleanField(label="Requires Encryption", required=False)
    noremoteaccess = forms.BooleanField(label="No Remote Access", required=False)
        
    class Meta:
        model = Tbldsas

class DataOwnerCreateForm(forms.Form):
    dataownername = forms.CharField(label="Data Owner Name", max_length=100)
    dataowneremail = forms.CharField(label="Data Owner Email", max_length=50, required=False)
        
    class Meta:
        model = Tbldsadataowners

class TransferSearchForm(forms.Form):
    projectnumber = forms.ModelChoiceField(label="Project Number", queryset=Tblproject.objects.filter(validto__isnull=True).order_by("projectnumber"), to_field_name="projectnumber", required=False)
    requesttype = forms.ModelChoiceField(label="Request Type", queryset=Tlktransferrequesttypes.objects.filter(validto__isnull=True).order_by("requesttypelabel"), required=False)
    requestedby = forms.ModelChoiceField(label="Requested By", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber", required=False)
    reviewedby = forms.ModelChoiceField(label="Reviewed By", queryset=Tbluser.objects.filter(validto__isnull=True, priviledged=True).order_by("firstname", "lastname"), to_field_name="usernumber", required=False)
    reviewdate = forms.DateTimeField(label="Review Date", widget = DateInput(), required=False)
        
    class Meta:
        model = Tbltransferrequest

class TransferForm(forms.Form):
    requestid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    projectnumber = forms.ModelChoiceField(label="Project Number", queryset=Tblproject.objects.filter(validto__isnull=True).order_by("projectnumber"), to_field_name="projectnumber")
    requesttype = forms.ModelChoiceField(label="Request Type", queryset=Tlktransferrequesttypes.objects.filter(validto__isnull=True).order_by("requesttypelabel"))
    requestedby = forms.ModelChoiceField(label="Requested By", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber")
    requesternotes = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "placeholder": "Requester note..."}), label="Requester Note", max_length=500, required=False)
    reviewedby = forms.ModelChoiceField(label="Reviewed By", queryset=Tbluser.objects.filter(validto__isnull=True, priviledged=True).order_by("firstname", "lastname"), to_field_name="usernumber")
    reviewdate = forms.DateTimeField(label="Review Date", widget = DateInput())
    reviewnotes = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "placeholder": "Reviewer note..."}), label="Reviewer Note", max_length=500, required=False)
    transfermethod = forms.ModelChoiceField(label="Transfer Method", queryset=Tlkfiletransfermethods.objects.filter(validto__isnull=True).order_by("methodlabel"))
    transferfrom = forms.CharField(label="Transfer From", max_length=250)
    transferto = forms.CharField(label="Transfer To", max_length=250)
    dsareviewed = forms.ModelChoiceField(widget=forms.Select(attrs={'style': 'width:250px'}), label="DSA Reviewed", queryset=Tbldsas.objects.filter(validto__isnull=True).order_by("dsaname"), to_field_name="documentid")
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    def clean(self):
            cleaned = super().clean()

            reviewdate = self.cleaned_data.get("reviewdate")
            if reviewdate and reviewdate > timezone.now():
                self.add_error(None, "Review Date cannot be later than today")

            return cleaned

    class Meta:
        model = Tbltransferrequest

class TransferfileForm(forms.Form):
    fileid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    requestid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    filename = forms.CharField(label="Filename", max_length=300)
    trefilepath = forms.CharField(label="TRE Filepath", max_length=200)
    datarepofilepath = forms.CharField(label="Data Repo Filepath", max_length=200)
    transferaccepted = forms.BooleanField(label="Accepted", required=False)
    rejectionnotes = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "placeholder": "Rejection note..."}), label="Rejection Note", max_length=500, required=False)
    # rejectionnotes = forms.CharField(label="Filename", max_length=500, required=False)
    assetid = forms.ModelChoiceField(widget=forms.Select(attrs={'style': 'width:250px'}), label="Asset", queryset=Tbltransferfileasset.objects.filter().order_by("assetname"), required=False)
    new_asset = forms.CharField(label="Or create a new one", required=False)
    validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    def clean(self):
            cleaned = super().clean()

            asset = cleaned.get("assetid")
            add_asset = cleaned.get("new_asset", "").strip()
            if asset is not None and add_asset:
                self.add_error(None, "Cannot select existing Asset and add new Asset")
            if asset is None and add_asset:
                asset, created = Tbltransferfileasset.objects.get_or_create(assetname=add_asset)
            cleaned["assetid"] = asset

            rejectionnotes = cleaned.get("rejectionnotes").strip()
            transferaccepted = cleaned.get("transferaccepted")
            if (rejectionnotes is None or rejectionnotes == "") and transferaccepted is False:
                self.add_error(None, "Must provide rejection reason for file(s) not accepted")
            if rejectionnotes and transferaccepted is True:
                self.add_error(None, "Rejection Notes added to accepted File(s)")

            return cleaned

    class Meta:
        model = Tbltransferfile

class TransferfileassetForm(forms.Form):
    assetid = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    assetname = forms.CharField(label="Asset Name", max_length=500, required=False)
    # dataowner = forms.CharField(label="Data Owner", max_length=100, required=False)
    # validfrom=  forms.DateTimeField(widget = forms.HiddenInput(), required=False) 
    # validto= forms.DateTimeField(widget = forms.HiddenInput(), required=False)
    # createdby= forms.CharField(widget = forms.HiddenInput(), required=False, max_length=50)

    class Meta:
        model = Tbltransferfileasset
