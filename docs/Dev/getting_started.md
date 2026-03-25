---
layout: default
title: Getting Started
nav_order: 1
parent: Development
has_children: false
---

- TOC
{:toc}

# Useful resources
Getting started:
[https://absolutecodeworks.com/python-django-crud-sample-with-sql-server](https://absolutecodeworks.com/python-django-crud-sample-with-sql-server)

Database connectivity:
[https://djangoadventures.com/how-to-integrate-django-with-existing-database/](https://djangoadventures.com/how-to-integrate-django-with-existing-database/)

# First steps!

Create a conda env and installed pyodbc and django, generate a requirements.txt. Will need other packages I'm sure.

Create Django Project (LASER)  
```python
django-admin startproject LASER .
```

Create Django App (Prism)  

```python
python manage.py startapp Prism
```

Add Prism app to list of `INSTALLED_APPS` in Project settings.py  
```python
INSTALLED_APPS = [
    ...
    'Prism',
]
```

Create html template file (/templates/projects.html)


Add view of `projects.html` to views.py
```python
def projects(request):
    return render(request, 'projects.html')
```

Create urls.py in App directory (/Prism)  
```python
from django.urls import path
from . import views
urlpatterns = [
    path('', views.projects, name = 'projects')
]
```

Add reference to App URLs (urls.py) in Project URLs (urls.py).
Need to import `include` function from `django.urls`. 
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Prism.urls'))
]
```

Start the server with: 
```python
python manage.py runserver
```

# Connect to existing database and create models

Need to install `mssql-django` package to connect to Azure SQL Database, Django built-in database backends only include postgresql, mysql, sqlite3 & oracle.

Edit Project settings.py and set DATABASES to point to existing database:  
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': <db_name>,
        'USER': <user_name>,
        'PASSWORD': <password>,
        'HOST': <server_name>'.database.windows.net',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
        }
    }
}
```

Automagically create Django models for all tables in existing database:  
```python 
python manage.py inspectdb > models.py
```

Once gernerated need to check to ensure foriegn key 'on_delete' behaviour is proper. It wasn't for me, so changed all `DO_NOTHING` to `PROTECT` (which is Django equivalent of SQL `RESTRICT`).  

For Django to manage table schema automatically, need to remove the `managed` attribute from each generated model. I don't want to do this just yet, if ever...

Place the `models.py` file in the App directory. 

Django automagically creates the migrations scripts:  
```python
python manage.py makemigrations
```

To apply the scripts run:
```python
python manage.py migrate --fake-initial
```  
The `--fake-initial` flag lets Django skip migrations where the table already exists. 

The Django user needs permissions to create the django_migrations table on first run.  

Now we should be running as if Django was managing the database from the start...

# Models & Views

Because we're now using Django models to define the SQL tables, we can leverage foreign keys to present values instead of keys.  

To do this, when querying the model from the view, append `__lookupTableFieldName` to the fact table field name. For example,  

```python
def projects(request):
    projects = Tblproject.objects.filter(
            validto__isnull=True
        ).values(
            "pid"
            , "projectnumber"
            , "projectname"
            , "stage__pstagedescription"
            , "pi"
            , "faculty__facultydescription"
        ).order_by("projectnumber")
    return render(request, 'projects.html', {'projects':projects})
```

It's possible to use `.annotate()` to add fields to query resultsets in view. For example can create `fullname` field from `firstname` & `lastname`. Don't even need to include `firstname` & `lastname` in the returned resultset. This only works if the fields you're using already exist in the database.  
```python
from django.db.models import Value
from django.db.models.functions import Concat
...
pi_user = Tbluser.objects.filter(
        validto__isnull=True
        , usernumber=project['pi']
    ).values(
        'usernumber'
    ).annotate(
        pi_fullname = Concat('firstname', Value(' '), 'lastname')
    ).get()
```

## Django relations and Type 2 SCD  
I've not found a way to define relationships between `Tbluser` model and user fields in the `Tblproject` model (eg `pi` and `leadapplicant`) whilst maintaining the desired Type 2 SCD behaviour of the database. The issue is that the primary key of `Tbluser` isn't used to identify an individual user; Type 2 SCD demands that we implement a surrogate key `usernumber` that's only unique when `validto` is null.  

I've tried defining the user fields of `Tblproject` as `ForeignKey` or `ManyToManyField` with a `db_constraint=False` flag but that just straight up didn't work.  

I've tried using a proxy table with custom methods to make data from `Tbluser` model available from an instance of `Tblproject` model in the View. That worked but the way Django functions it was necessary to iterate over every record in the view to populate and it seemed to make a database call every single time. The performance tanked and while it may be feasible for a single project, when listing many/all of them it was untenable.  

In the end I went with a single call to the model with the related data and converted it to a pandas DataFrame, using that to iterate over and update each record (eg replacing the `usernumber` value stored in `Tblproject.pi` with a concatenated full name in the `projects` view that lists all projects).  

Struggling to exclude model fields on SQL insert when updating records. I want to do this because I'd prefer the SQL Database to handle populating certain data fields like `ValidFrom` and `CreatedBy` with their database defaults, rather than having Django generate those values. Currently I am having to populate them in Django and insert the non-default values as all attempts at exclusion have just led to insertion of nulls... 

I have actually found a way to allow the database to populate default values but it's relatively undesired for our purposes due to the way that the app connects to the database. We've simply got to exclude the fields from the models. Don't let Django see them at all! Would probably work just fine for `[ValidFrom] = getdate()` fields but `[CreatedBy] = suser_sname` appears to populate with the Object ID of the Identity used to make the connection (ie the Web Service if in deployment). Functionally useless!  

# Forms

`ModelChoiceField` takes actual model objects, do not use `.values` or `values_list`.  
It uses the primary keys of the model objects for key values and their string representation as their label values.  
In order to not have keys for label we need to override the string representations in the model:
```python
class Tlkstage(models.Model):
    stageid = models.IntegerField(db_column='StageID', primary_key=True) 
    stagedescription = models.CharField(db_column='pStageDescription', max_length=25)

    def __str__(self):
        return self.stagedescription
```

`DateField` seems to default to text when rendered to html!  
To render as actual date pickers we can override their widgets in `__init__`, after creating a `DateInput` class:
```python
class DateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)

class MyForm(forms.Form):
    ...
    def __init__(self, *args, **kwargs):
        self.fields["datefield"].widget = DateInput()
```

Form fields can be prepopulated with details from a queryset using the `initial` argument when instantiating the form in the view.  
```python
form = MyForm(initial=queryset)
```

Some form fields seem to struggle with this when the field value comes from a `ForeignKey` field in the model, noticeably `ModelChoiceField`. ~~This can be overcome by overriding the `initial` arguments in the `__init__` of the form:~~  

<strike>

```python
class MyForm(forms.Form):
    ...
    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)
        updated_initial = initial_arguments
        if initial_arguments:
            formfield = initial_arguments.get('formfield_id',None)
            if formfield:
                    updated_initial['formfield'] = formfield
        kwargs.update(initial=updated_initial)
        super(ProjectForm, self).__init__(*args, **kwargs)
```

</strike>

While this did work it was utterly unneccessary! The real issue was simply that the fields in the form needed to be named to match the Primary Key of the related fields in the model. So, for example, the `stage` field in the `Tblproject` model is a ForeignKey to `Tlkstage`, which has the Primary Key `stage_id`. So declaring the `stage_id` field in the `ProjectForm` form (instead of `stage`) meant that it was able to receive current value from `initial`.  

Seems obvious now I look again at the code snippet above... I'm taking the value of `formfield_id` and popping it into `formfield`. Just use `formfield_id`!

`PI` & `LeadApplicant` fields are ModelChoiceFields again! They use a queryset from `Tbluser` model (with the overridden `__str__` frunction) to define permitted values and the flag `to_field_name="usernumber"` to prevent the use of the Primary Key for TblUser being used. Each Surrogate Key `usernumber` is (should be!) unique when `ValidTo` is null so need to ensure that's included in the filter defining the queryset. 

```python
pi = forms.ModelChoiceField(label="PI", queryset=Tbluser.objects.filter(validto__isnull=True).order_by("firstname", "lastname"), to_field_name="usernumber")
    
```
