from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.apps import apps
from django.db import transaction
from django.db.models import Max, Count, OuterRef, Subquery, Q, Case, When, BooleanField, Value, CharField
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required 
from django.forms import formset_factory
from .models import Tblproject, Tbluser, Tblprojectnotes, Tblprojectdocument, Tlkdocuments, Tblprojectplatforminfo \
    , Tblprojectdatallocation, Tbluserproject, Tblkristal, Tblprojectkristal, Tlkstage, Tlkfaculty, Tlkclassification \
    , Tlkuserstatus, Tblusernotes, Tblprojectkristal, tlkGrantStage, Tlklocation, Tblkristalnotes, Tbldsas, Tbldsanotes \
    , Tbldsasprojects, Tbldsadataowners, Tlktransferrequesttypes, Tbltransferrequest, Tbltransferfile, Tbltransferfileasset \
    , Tbldsdpcohort, tblPortfolioPlus
from .forms import  ProjectSearchForm, ProjectForm, ProjectNotesForm, ProjectDocumentsForm, ProjectPlatformInfoForm \
    , ProjectDatAllocationForm, UserSearchForm, UserForm, UserProjectForm, UserNotesForm, KristalForm, ProjectKristalForm \
    , GrantSearchForm, GrantNotesForm, DsaForm, DsaNotesForm, ProjectDsaForm, DsaSearchForm, DataOwnerCreateForm, TransferSearchForm \
    , TransferForm, TransferfileForm, DSDPCohortForm, PortfolioPlusForm
import pandas as pd
import numpy as np
from collections import namedtuple
import json
from decimal import Decimal, ROUND_HALF_UP

def index(request):
    return render(request, 'Prism/index.html')

@login_required
@permission_required(["Prism.view_tbluser", "Prism.view_tblproject", "Prism.view_tbldsdpcohort"], raise_exception=True)
def projects(request):
    query = request.GET

    filter_query = {}
    advanced_filter_query = {}
    user_filter_query = {}
    filter_list = []

    if query is not None and query != '':
        for key in query:
            value = query.get(key)
            if value != '':
                if key == 'q':
                    filter_query['projectname__icontains'] = value
                    filter_query['projectnumber__icontains'] = value
                    filter_list.append(f"Project Number or Name contains '{value}'")
                if key == 'stage_id':
                    advanced_filter_query['stage__stageid__iexact'] = value
                    filter_list.append(f"Stage is '{Tlkstage.objects.get(stageid=value)}'")
                if key == 'classification_id':
                    advanced_filter_query['classification__classificationid__iexact'] = value
                    filter_list.append(f"Risk Class is '{Tlkclassification.objects.get(classificationid=value)}'")
                if key == 'user':
                    user_filter_query['pi__iexact'] = value
                    user_filter_query['leadapplicant__iexact'] = value
                    filter_list.append(f"PI or Lead Applicant is '{Tbluser.objects.get(usernumber=value, validto__isnull=True)}'")
                if key == 'faculty_id':
                    advanced_filter_query['faculty__facultyid__iexact'] = value
                    filter_list.append(f"Faculty is '{Tlkfaculty.objects.get(facultyid=value)}'")
                if key == 'laser':
                    advanced_filter_query['laser__iexact'] = True
                    filter_list.append(f"LASER = {True}")
                if key == 'internship':
                    advanced_filter_query['internship__iexact'] = True
                    filter_list.append(f"DSDP = {True}")
                if key == 'cohort':
                    advanced_filter_query['projectnumber__in'] = Tbldsdpcohort.objects.filter(cohort=value).values_list('projectnumber')
                    filter_list.append(f"DSDP Cohort = {value}")

    projects = Tblproject.objects.filter(
            Q(**filter_query, _connector=Q.OR)
            , Q(**advanced_filter_query, _connector=Q.AND)
            , Q(**user_filter_query, _connector=Q.OR)
            , validto__isnull=True
        ).values(
            "pid"
            , "projectnumber"
            , "projectname"
            , "laser"
            , "internship"
            , "stage__pstagedescription"
            , "classification__classificationdescription"
            , "pi"
            , "leadapplicant"
            , "faculty__facultydescription"
        ).order_by("projectnumber")

    users = Tbluser.objects.filter(
            validto__isnull=True
            ).values()
    users_df = pd.DataFrame(users)

    dsdp_cohort = Tbldsdpcohort.objects.values().order_by('projectnumber', 'cohort')
    dsdp_df = pd.DataFrame(dsdp_cohort)
    dsdp_df = dsdp_df.groupby(['projectnumber'])['cohort'].apply(', '.join).reset_index()

    for project in projects:
        if project['pi'] is not None:
            pi_index = users_df.index[users_df['usernumber'] == project['pi']].tolist()
            pi_name = f"{users_df.at[pi_index[0],'firstname']} {users_df.at[pi_index[0],'lastname']}"
            project.update(pi=pi_name)
        if project['leadapplicant'] is not None:
            leadapplicant_index = users_df.index[users_df['usernumber'] == project['leadapplicant']].tolist()
            leadapplicant_name = f"{users_df.at[leadapplicant_index[0],'firstname']} {users_df.at[leadapplicant_index[0],'lastname']}"
            project.update(leadapplicant=leadapplicant_name)
        if project['projectnumber'] in dsdp_df['projectnumber'].values:
            dsdp_index = dsdp_df.index[dsdp_df['projectnumber'] == project['projectnumber']].tolist()
            cohort = f"{dsdp_df.at[dsdp_index[0],'cohort']}"
            project.update(portfolionumber=cohort)

    filter_string = ", ".join(filter_list)
    project_search_form = ProjectSearchForm()

    return render(request, 'Prism/projects.html', {'projects': projects
                                                   ,'project_form': project_search_form
                                                   ,'searchterms': filter_string})

@login_required
@permission_required(["Prism.view_tblproject", "Prism.add_tblproject", "Prism.change_tblproject"
                      , "Prism.view_tblprojectdocument"
                      , "Prism.view_tbluser", "Prism.view_tbluserproject", "Prism.add_tbluserproject", "Prism.change_tbluserproject"
                      , "Prism.view_tblkristal", "Prism.view_tblprojectkristal", "Prism.add_tblprojectkristal", "Prism.change_tblprojectkristal"
                      , "Prism.view_tblprojectdatallocation", "Prism.add_tblprojectdatallocation", "Prism.change_tblprojectdatallocation"
                      , "Prism.view_tblprojectplatforminfo", "Prism.add_tblprojectplatforminfo", "Prism.change_tblprojectplatforminfo"
                      , "Prism.view_tblprojectnotes", "Prism.add_tblprojectnotes", "Prism.change_tblprojectnotes"
                      , "Prism.view_tbldsdpcohort", "Prism.add_tbldsdpcohort"], raise_exception=True)
def project(request, projectnumber):
    # Build forms
    
    ## PROJECT ##
    project = Tblproject.objects.filter(
        validto__isnull=True
        , projectnumber=projectnumber
    ).values(
    ).get()         # get() with no arguments will raise an exception if the queryset doesn't contain exactly one item

    ## PROJECT DOCS ##
    project_docs = Tblprojectdocument.objects.filter(
        validto__isnull=True
        , projectnumber=projectnumber
    ).values(            
    ).order_by("documenttype", "versionnumber")
    
    # Important that these top level key names match the values of [DocumentDescription] stored in the database table [tlkDocuments]
    p_docs={
        "Project Proposal":{'url':'proposal', 'status':''}
        ,"Data Management Plan":{'url':'dmp', 'status':''}
        ,"Risk Assessment":{'url':'ra', 'status':''}
    }
    for doc in p_docs:
        if project_docs.filter(documenttype__documentdescription=doc
                            , accepted__isnull=False).exists():
            p_docs[doc]["status"] = "accepted"
        elif project_docs.filter(documenttype__documentdescription=doc
                            , accepted__isnull=True).exists():
            p_docs[doc]["status"] = "present"
        else: 
            p_docs[doc]["status"] = "absent"

    ## PROJECT MEMBERSHIP ##
    # Using OuterRef & Subquery to perform a lookup against Tblproject on Tbluserproject's projectnumber and add it to the model with annotate 
    firstnames = Tbluser.objects.filter(
        validto__isnull=True
        ,usernumber=OuterRef("usernumber")
    ).values("firstname")

    lastnames = Tbluser.objects.filter(
        validto__isnull=True
        ,usernumber=OuterRef("usernumber")
    ).values("lastname")

    project_membership = Tbluserproject.objects.filter(
            validto__isnull=True
            , projectnumber=projectnumber
    ).values(
    ).annotate(firstname = Subquery(firstnames)
               ,lastname = Subquery(lastnames)
    ).order_by("firstname", "lastname")

    ## DSDP Cohort ##
    dsdp_cohort = Tbldsdpcohort.objects.filter(
        projectnumber=projectnumber
    ).values(            
    ).order_by("cohort")

    ## KRISTAL REFERENCES ##
    # Using OuterRef & Subquery to perform a lookup against Tblprojectkristal on Tbluserproject's projectnumber and add it to the model with annotate 
    projectkristalids = Tblprojectkristal.objects.filter(
        validto__isnull=True
        , projectnumber=projectnumber
        , kristalnumber=OuterRef("kristalnumber")
    ).values("projectkristalid")

    kristal_refs = Tblkristal.objects.filter(
        kristalnumber__in = Tblprojectkristal.objects.filter(
            validto__isnull=True
            , projectnumber=projectnumber
            ).values_list('kristalnumber')
        ,validto__isnull=True
    ).values(
    ).annotate(projectkristalid=Subquery(projectkristalids)
    ).order_by("kristalref")

    ## DAT ALLOCATION ##
    project_dat_allocation = Tblprojectdatallocation.objects.filter(
        validto__isnull=True
        , projectnumber=projectnumber
    ).values("projectdatallocationid", "fromdate", "todate", "fte", "account"
    ).order_by("-fromdate")

    ## PROJECT PLATFORM DETAILS ##
    project_platform_info = Tblprojectplatforminfo.objects.filter(
        validto__isnull=True
        , projectnumber=projectnumber
    ).values("projectplatforminfoid", "platforminfoid__platforminfodescription", "projectplatforminfo"
    ).order_by("platforminfoid", "projectplatforminfo")

    ## PROJECT NOTES ##
    query = request.GET.get("search_notes")
    filter_query = {}
    if query is not None and query != '':
        filter_query['pnote__icontains'] = query
    
    project_notes = Tblprojectnotes.objects.filter(
        Q(**filter_query, _connector=Q.OR)
        , projectnumber=projectnumber
    ).values(
    ).order_by("-created")

    paginator = Paginator(project_notes, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ## CREATE FORMS ##
    project_form = ProjectForm(initial=project, prefix='project')
    p_dat_allocation_form = ProjectDatAllocationForm(prefix='p_dat_allocation')
    p_notes_form = ProjectNotesForm(prefix='p_note')
    p_platform_info_form = ProjectPlatformInfoForm(prefix='p_platform')
    p_user_form = UserProjectForm(prefix='p_user')
    p_user_form.initial['projectnumber'] = projectnumber
    dsdp_cohort_form = DSDPCohortForm(prefix='p_dsdp_cohort')
    p_kristal_form = KristalForm(prefix='p_kristal')

    project_numbers = Tblproject.objects.filter(
        validto__isnull=True
    ).values("projectnumber"
    ).order_by("projectnumber")

    ## DATA VALIDATION ##
    # Populated on GET Request
    custom_errors = []

    ## SET CONTEXT ##
    context = {'project':project
        , 'form':project_form
        , 'project_numbers': project_numbers
        , 'p_docs': p_docs
        , 'dat_allocation': project_dat_allocation
        , 'custom_errors': custom_errors
        , 'dat_allocation_form': p_dat_allocation_form
        , 'platforminfo': project_platform_info
        , 'platform_form': p_platform_info_form
        , 'members': project_membership
        , 'dsdp_cohort': dsdp_cohort
        , 'dsdp_cohort_form': dsdp_cohort_form
        , 'p_user_form': p_user_form
        , 'grants': kristal_refs
        , 'p_kristal_form': p_kristal_form
        , 'new_note': p_notes_form
        , 'notes':page_obj
        , 'notes_filter' : query}

    # Then check if POST or GET

    if request.method == "POST":
        if 'project-pid' in request.POST:
            project_form = ProjectForm(request.POST, prefix='project')
            if project_form.is_valid():
                pID = project_form.cleaned_data['pid']
                insert = Tblproject(
                    projectnumber = projectnumber
                    ,projectname = project_form.cleaned_data['projectname']
                    ,portfolionumber = project_form.cleaned_data['portfolionumber']
                    ,stage = project_form.cleaned_data['stage_id']
                    ,classification = project_form.cleaned_data['classification_id']
                    ,datrag = project_form.cleaned_data['datrag']
                    ,projectedstartdate = project_form.cleaned_data['projectedstartdate']
                    ,projectedenddate = project_form.cleaned_data['projectedenddate']
                    ,startdate = project_form.cleaned_data['startdate']
                    ,enddate = project_form.cleaned_data['enddate']
                    ,pi = project_form.cleaned_data['pi'].usernumber
                    ,leadapplicant = project_form.cleaned_data['leadapplicant'].usernumber
                    ,faculty = project_form.cleaned_data['faculty_id']
                    ,lida = project_form.cleaned_data['lida']
                    ,internship = project_form.cleaned_data['internship']
                    ,dspt = project_form.cleaned_data['dspt']
                    ,iso27001 = project_form.cleaned_data['iso27001']
                    ,laser = project_form.cleaned_data['laser']
                    ,irc = project_form.cleaned_data['irc']
                    ,seed = project_form.cleaned_data['seed']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                
                # Fetch existing project record
                existing_project = Tblproject.objects.filter(
                    validto__isnull=True
                    , projectnumber=projectnumber
                ).values(
                ).get() 

                with transaction.atomic():
                    # Only save record if fields have changed
                    if recordchanged(existing_record=existing_project, form_set=insert):
                        insert.save(force_insert=True)

                        delete = Tblproject(
                            pid = pID
                            ,validto = timezone.now()
                        )
                        delete.save(update_fields=["validto"])
                    
                        messages.success(request, 'Project updated successfully.')

                    # Add PI and/or Lead Applicant to project membership if not already present
                    if not project_membership.filter(usernumber=insert.pi).exists():
                        insert_user_project = Tbluserproject(
                            usernumber = insert.pi
                            ,projectnumber = projectnumber
                            ,validfrom = timezone.now()
                            ,validto = None
                            ,createdby = request.user
                        )
                        insert_user_project.save(force_insert=True)
                    if not project_membership.filter(usernumber=insert.leadapplicant).exists():
                        insert_user_project = Tbluserproject(
                            usernumber = insert.leadapplicant
                            ,projectnumber = projectnumber
                            ,validfrom = timezone.now()
                            ,validto = None
                            ,createdby = request.user
                        )
                        insert_user_project.save(force_insert=True)

                    return HttpResponseRedirect(f"/project/{projectnumber}")
            else:
                context['form']=project_form

        elif 'p_dat_allocation-projectdatallocationid' in request.POST:
            p_dat_allocation_form = ProjectDatAllocationForm(request.POST, prefix='p_dat_allocation')
            if p_dat_allocation_form.is_valid():
                insert_dat_allocation = Tblprojectdatallocation(
                    projectnumber = projectnumber
                    ,fromdate = p_dat_allocation_form.cleaned_data['fromdate']
                    ,todate = p_dat_allocation_form.cleaned_data['todate']
                    ,fte = p_dat_allocation_form.cleaned_data['fte']
                    ,account = p_dat_allocation_form.cleaned_data['account']
                    ,validfrom = timezone.now()
                    ,createdby = request.user
                )
                insert_dat_allocation.save(force_insert=True)
                messages.success(request, 'DAT Allocation added successfully.')
                return HttpResponseRedirect(f"/project/{projectnumber}")
            else:
                context['dat_allocation_form']=p_dat_allocation_form

        elif 'p_note-pnote' in request.POST:
            p_notes_form = ProjectNotesForm(request.POST, prefix='p_note')
            if p_notes_form.is_valid():
                insert_note = Tblprojectnotes(
                    projectnumber = projectnumber
                    ,pnote = p_notes_form.cleaned_data['pnote']
                    ,created = timezone.now()
                    ,createdby = request.user
                )
                insert_note.save(force_insert=True)
                messages.success(request, 'Project note added successfully.')
                return HttpResponseRedirect(f"/project/{projectnumber}")
            else:
                context['new_note']=p_notes_form

        elif 'p_platform-platforminfoid' in request.POST:
            p_platform_info_form = ProjectPlatformInfoForm(request.POST, prefix='p_platform')
            if p_platform_info_form.is_valid():
                insert_platform_info = Tblprojectplatforminfo(
                    projectnumber = projectnumber
                    ,platforminfoid = p_platform_info_form.cleaned_data['platforminfoid']
                    ,projectplatforminfo = p_platform_info_form.cleaned_data['projectplatforminfo']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                insert_platform_info.save(force_insert=True)
                messages.success(request, 'Project platform info added successfully.')
                return HttpResponseRedirect(f"/project/{projectnumber}")
            else:
                context['platform_form']=p_platform_info_form
        
        elif 'p_user-usernumber' in request.POST:
            p_user_form = UserProjectForm(request.POST, prefix='p_user')
            if p_user_form.is_valid():
                insert_user_project = Tbluserproject(
                    usernumber = p_user_form.cleaned_data['usernumber'].usernumber
                    ,projectnumber = projectnumber
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                insert_user_project.save(force_insert=True)
                messages.success(request, 'User added to Project successfully.')
                return HttpResponseRedirect(f"/project/{projectnumber}")
            else:
                context['p_user_form']=p_user_form
        
        elif 'p_dsdp_cohort-cohort' in request.POST:
            dsdp_cohort_form = DSDPCohortForm(request.POST, prefix='p_dsdp_cohort')
            if dsdp_cohort_form.is_valid():
                insert_dsdp_cohort = Tbldsdpcohort(
                    cohort = dsdp_cohort_form.cleaned_data['cohort']
                    ,projectnumber = projectnumber
                )
                insert_dsdp_cohort.save()
                messages.success(request, 'DSDP Cohort added to Project successfully.')
                return HttpResponseRedirect(f"/project/{projectnumber}")
            else:
                context['dsdp_cohort_form']=dsdp_cohort_form

        elif 'p_kristal-kristalref' in request.POST:
            kristal_form = KristalForm(request.POST, prefix='p_kristal')
            if kristal_form.is_valid():
                # Check if Kristal Ref alrady exists in Tblkristal
                if not Tblkristal.objects.filter(validto__isnull=True, kristalref = kristal_form.cleaned_data['kristalref']).exists():
                    # If it doesn't insert new record to Tblkristal
                    # Get latest KristalNumber from database model and iterate up by one for new KristalNumber
                    max_kristalnumber = Tblkristal.objects.filter(
                        validto__isnull=True
                    ).aggregate(Max("kristalnumber"))
                    new_kristalnumber = max_kristalnumber['kristalnumber__max'] + 1

                    insert_new_kristal = Tblkristal(
                        kristalnumber = new_kristalnumber
                        ,kristalref = kristal_form.cleaned_data['kristalref']
                        ,validfrom = timezone.now()
                        ,validto = None
                        ,createdby = request.user
                    )

                    insert_new_kristal.save(force_insert=True)

                # Then insert new record to Tblprojectkristal
                kristalnumber = Tblkristal.objects.filter(validto__isnull=True, kristalref=kristal_form.cleaned_data['kristalref']).values('kristalnumber').get()['kristalnumber']
                # Use form validation to prevent duplicate entries
                insert_project_kristal_form = ProjectKristalForm(data={
                    'projectnumber' : projectnumber
                    ,'kristalnumber' : kristalnumber
                    })

                if insert_project_kristal_form.is_valid():
                    insert_project_kristal = Tblprojectkristal(
                        projectnumber = projectnumber
                        ,kristalnumber = kristalnumber
                        ,validfrom = timezone.now()
                        ,validto = None
                        ,createdby = request.user
                    )
                    insert_project_kristal.save(force_insert=True)

                    messages.success(request, 'Kristal Ref added to Project successfully.')
                    return HttpResponseRedirect(f"/project/{projectnumber}")
                else: 
                    # Copy ProjectKristalForm non_field_errors to KristalForm used on page
                    kristal_form.add_error(None, insert_project_kristal_form.errors)
                    context['p_kristal_form']=kristal_form
            else:
                context['p_kristal_form']=kristal_form

        return render(request, 'Prism/project.html', context)

    if request.method == 'GET':
        ## DATA VALIDATION ##
        # For information purposes only. 
        # Validation across/between forms or where errors not sufficient to prevent form submission.

        # Do we have a DAT Allocation?
        if not project_dat_allocation:
            custom_errors.append("Missing DAT Allocation information")

        # Are there missing accounts for DAT Recoveries?
        for item in project_dat_allocation:
            if item['account'] == '':
                custom_errors.append("Missing DAT Allocation Account information")
                break
        
        # Are there overlapping or missing periods of DAT Support?
        if project_dat_allocation:
            df = pd.DataFrame(project_dat_allocation)
            Range = namedtuple('Range', ['start', 'end'])
            for index, row in df.iterrows():
                if index > 0:
                    r1 = Range(start=row['fromdate'], end=row['todate'])
                    r2 = Range(start=df['fromdate'].iloc[index-1], end=df['todate'].iloc[index-1])
                    latest_start = max(r1.start, r2.start)
                    earliest_end = min(r1.end, r2.end)
                    delta = (earliest_end - latest_start).days + 1
                    if delta > 0:
                        custom_errors.append("There are overlapping periods of DAT Allocation")
                    if delta < 0:
                        custom_errors.append("There are missing periods of DAT Allocation")
        
        # Does DAT Support period align with Project Start/End dates?
        if project_dat_allocation:
            earliest_dat_allocation = project_dat_allocation.order_by('fromdate').first()['fromdate']
            latest_dat_allocation = project_dat_allocation.order_by('todate').last()['todate']
            if project['projectedstartdate'] is not None and earliest_dat_allocation is not None and project['startdate'] is None:
                if earliest_dat_allocation > project['projectedstartdate']:
                    custom_errors.append("DAT Allocation starts after Projected Start Date")
                if earliest_dat_allocation < project['projectedstartdate']:
                    custom_errors.append("DAT Allocation starts before Projected Start Date")
            if project['projectedenddate'] is not None and latest_dat_allocation is not None and project['enddate'] is None:
                if latest_dat_allocation > project['projectedenddate']:
                    custom_errors.append("DAT Allocation continues after Projected End Date")
                if latest_dat_allocation < project['projectedenddate']:
                    custom_errors.append("DAT Allocation ends before Projected End Date")
            if project['startdate'] is not None and earliest_dat_allocation is not None:
                if earliest_dat_allocation > project['startdate']:
                    custom_errors.append("DAT Allocation starts after Start Date")
                if earliest_dat_allocation < project['startdate']:
                    custom_errors.append("DAT Allocation starts before Start Date")
            if project['enddate'] is not None and latest_dat_allocation is not None:
                if latest_dat_allocation > project['enddate']:
                    custom_errors.append("DAT Allocation ends after End Date")
                if latest_dat_allocation < project['enddate']:
                    custom_errors.append("DAT Allocation ends before End Date")

        if project['stage_id'] == 3 and project['laser']:
            for doc in p_docs:
                if p_docs[doc]['status'] == "absent" or p_docs[doc]['status'] == "present":
                    custom_errors.append(f"Project is 'Active' without a required {doc}")

        # Do we have a Kristal Reference?
        if not kristal_refs:
            custom_errors.append("Missing Kristal Reference information")

        # Is project in a DSDP Cohort without DSDP checked?
        if not project['internship'] and dsdp_cohort:
            custom_errors.append("Project is a member of a DSDP Cohort but Type:DSDP = False")
        # Is project not in a DSDP Cohort with DSDP checked?
        if project['internship'] and not dsdp_cohort:
            custom_errors.append("Project is not a member of a DSDP Cohort but Type:DSDP = True")

        return render(request, 'Prism/project.html', context)

@login_required
@permission_required("Prism.add_tblproject", raise_exception=True)
def projectcreate(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():

            # Get latest ProjectNumber from database model and iterate up by one for new ProjectNumber
            max_projectnumber = Tblproject.objects.filter(
                validto__isnull=True
                ,projectnumber__startswith='P'
            ).aggregate(Max("projectnumber"))
            new_projectnumber = 'P' + str('0000' + str(int(max_projectnumber['projectnumber__max'][-4:]) +1))[-4:]
            
            with transaction.atomic():
                insert = Tblproject(
                    projectnumber = new_projectnumber
                    ,projectname = form.cleaned_data['projectname']
                    ,portfolionumber = form.cleaned_data['portfolionumber']
                    ,stage = form.cleaned_data['stage_id']
                    ,classification = form.cleaned_data['classification_id']
                    ,datrag = form.cleaned_data['datrag']
                    ,projectedstartdate = form.cleaned_data['projectedstartdate']
                    ,projectedenddate = form.cleaned_data['projectedenddate']
                    ,startdate = form.cleaned_data['startdate']
                    ,enddate = form.cleaned_data['enddate']
                    ,pi = form.cleaned_data['pi'].usernumber
                    ,leadapplicant = form.cleaned_data['leadapplicant'].usernumber
                    ,faculty = form.cleaned_data['faculty_id']
                    ,lida = form.cleaned_data['lida']
                    ,internship = form.cleaned_data['internship']
                    ,dspt = form.cleaned_data['dspt']
                    ,iso27001 = form.cleaned_data['iso27001']
                    ,laser = form.cleaned_data['laser']
                    ,irc = form.cleaned_data['irc']
                    ,seed = form.cleaned_data['seed']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                insert.save(force_insert=True)

                # Add PI and/or Lead Applicant to project membership
                insert_user_project = Tbluserproject(
                    usernumber = insert.pi
                    ,projectnumber = new_projectnumber
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                insert_user_project.save(force_insert=True)

                if insert.pi != insert.leadapplicant:
                    insert_user_project = Tbluserproject(
                        usernumber = insert.leadapplicant
                        ,projectnumber = new_projectnumber
                        ,validfrom = timezone.now()
                        ,validto = None
                        ,createdby = request.user
                    )
                    insert_user_project.save(force_insert=True)

                return HttpResponseRedirect(f"/project/{new_projectnumber}")
        else:
            return render(request, 'Prism/project_new.html', {'form':form})   

    if request.method == 'GET':
        form = ProjectForm()
        return render(request, 'Prism/project_new.html', {'form':form})
    
def recordchanged(existing_record, form_set):
    # Compare existing record to form values
    record_changed = False
    for field in existing_record:
        if form_set._meta.get_field(field).primary_key or field == 'validfrom' or field == 'validto' or field == 'createdby':
            record_changed = record_changed
        elif existing_record[field] != getattr(form_set, field):
            record_changed = True
    return record_changed

@login_required
@permission_required(["Prism.view_tblprojectdocument", "Prism.add_tblprojectdocument", "Prism.change_tblprojectdocument"], raise_exception=True)
def projectdocs(request, projectnumber, doctype=None):
    filter_query = {}
    # Important that these values match the values of [DocumentDescription] stored in the database table [tlkDocuments]
    doctype_dict = {None:None
                    , 'proposal': 'Project Proposal'
                    , 'dmp': 'Data Management Plan'
                    , 'ra': 'Risk Assessment'}
    if doctype is not None:
        filter_query['documenttype__documentdescription'] = doctype_dict[doctype]

    project_docs = Tblprojectdocument.objects.filter(
            Q(**filter_query, _connector=Q.OR)
            , validto__isnull=True
            , projectnumber=projectnumber
        ).values(
            'pdid'
            ,'projectnumber'
            ,'documenttype__documentdescription'
            ,'versionnumber'
            ,'submitted'
            ,'accepted'
        ).order_by("documenttype", "versionnumber")

    # Initialise documenttype input if looking at single doctype
    if doctype is not None:
        doc_id = Tlkdocuments.objects.filter(
            validto__isnull=True
            ,documentdescription=doctype_dict[doctype]
        ).values(
            'documentid'
        ).get()
        project_docs_form=ProjectDocumentsForm(initial={'documenttype':doc_id['documentid']})
    else:
        project_docs_form=ProjectDocumentsForm()
    
    ## DATA VALIDATION ##
    # Populated on GET Request
    custom_errors = []
    
    context = {'project_docs':project_docs
        , 'project_docs_form': project_docs_form
        , 'projectnumber':projectnumber
        , 'doctype':doctype_dict[doctype]
        , 'doctypeurl':doctype
        , 'custom_errors': custom_errors}
    
    if request.method == "POST":
        project_docs_form=ProjectDocumentsForm(request.POST)
        if project_docs_form.is_valid():
            
            # Get latest VersionNumber from database model and iterate up by one for new VersionNumber
            max_versionnumber = Tblprojectdocument.objects.filter(
                validto__isnull=True
                ,projectnumber=projectnumber
                ,documenttype=project_docs_form.cleaned_data['documenttype']
            ).aggregate(Max("versionnumber"))
            if max_versionnumber['versionnumber__max'] is not None:
                new_versionnumber = int(max_versionnumber['versionnumber__max']) +1
            else:
                new_versionnumber = 1
            insert = Tblprojectdocument(
                projectnumber=projectnumber
                , documenttype=project_docs_form.cleaned_data['documenttype']
                , versionnumber=new_versionnumber
                , submitted=project_docs_form.cleaned_data['submitted']
                , accepted=project_docs_form.cleaned_data['accepted']
                , validfrom=timezone.now()
                , validto=None
                , createdby=request.user
                )
            insert.save(force_insert=True)
            if doctype:
                return HttpResponseRedirect(f"/project/{projectnumber}/docs/{doctype}")
            else:
                return HttpResponseRedirect(f"/project/{projectnumber}/docs")
        else:
            context['project_docs_form'] = project_docs_form
        return render(request, 'Prism/docs.html', context)

    if request.method == "GET":
        ## DATA VALIDATION ##
        # For information purposes only. 
        # Validation across/between forms or where errors not sufficient to prevent form submission.
        summary = project_docs.values('documenttype__documentdescription'
        ).annotate(
            accepted_count=Count('pdid', filter=Q(accepted__isnull=False), distinct=True)
            ,max_submitted=Max('submitted')
            ,max_accepted=Max('accepted')
        ).order_by()
        
        for doc_type in summary:
        # Is there > 1 Accepted for a Document Type?
            if doc_type['accepted_count'] > 1:
                custom_errors.append(f"There is more than one Accepted {doc_type['documenttype__documentdescription']}")
        # Is there a Submitted later than an Accepted?
            if doc_type['max_submitted'] is not None and doc_type['max_accepted'] is not None:
                if doc_type['max_submitted'] > doc_type['max_accepted']:
                    custom_errors.append(f"A {doc_type['documenttype__documentdescription']} has been Submitted since the last Accepted")
        
        return render(request, 'Prism/docs.html', context)
    
@login_required
@permission_required(["Prism.change_tblprojectdocument"], raise_exception=True)
def projectdocs_action(request, projectnumber, doctype, action, pdid):
    update_record=Tblprojectdocument.objects.filter(
        pdid=pdid
        , projectnumber=projectnumber
    ).values()

    if action == 'accept':
        update_record.update(accepted = timezone.now())
    elif action == 'withdraw':
        update_record.update(accepted = None)
    elif action == 'remove':
        update_record.update(validto = timezone.now())
    
    if doctype and doctype != 'None':
        return HttpResponseRedirect(f"/project/{projectnumber}/docs/{doctype}")
    else:
        return HttpResponseRedirect(f"/project/{projectnumber}/docs")

@login_required
@permission_required(["Prism.change_tblprojectplatforminfo"], raise_exception=True)
def projectplatforminfo_remove(request, projectnumber, projectplatforminfoid):
    update_record=Tblprojectplatforminfo.objects.filter(
        projectplatforminfoid=projectplatforminfoid
        , projectnumber=projectnumber
    ).values()
    update_record.update(validto = timezone.now())
    
    return HttpResponseRedirect(f"/project/{projectnumber}")

@login_required
@permission_required(["Prism.change_tblprojectdatallocation"], raise_exception=True)
def projectdatallocation_remove(request, projectnumber, projectdatallocationid):
    update_record=Tblprojectdatallocation.objects.filter(
        projectdatallocationid=projectdatallocationid
        , projectnumber=projectnumber
    ).values()
    update_record.update(validto = timezone.now())
    
    return HttpResponseRedirect(f"/project/{projectnumber}")

@login_required
@permission_required(["Prism.delete_tbldsdpcohort"], raise_exception=True)
def dsdpcohort_remove(request, projectnumber, dsdpcohortid):
    project_cohort = Tbldsdpcohort.objects.get(dsdpcohortid=dsdpcohortid)
    project_cohort.delete()
    return HttpResponseRedirect(f"/project/{projectnumber}")

@login_required
@permission_required(["Prism.view_tbluser"], raise_exception=True)
def projectuserdocs(request, projectnumber):
    twelve_months_ago = timezone.now() - timedelta(days=365)
    three_years_ago = timezone.now() - timedelta(days=365*3)
    
    project_user_docs = Tbluser.objects.filter(
        validto__isnull=True
        , usernumber__in=Tbluserproject.objects.filter(validto__isnull=True, projectnumber=projectnumber).values_list("usernumber")
    ).annotate(laseragreement_status=Case(
                    When(laseragreement__lt=timezone.now()
                        , then=Value('Received'))
                        , default=Value('Outstanding'), output_field=CharField())
        , dataprotection_status=Case(
            When(dataprotection__gt=twelve_months_ago
                , then=Value('Received'))
            , When(dataprotection__lt=twelve_months_ago
                ,then=Value('Expired'))
                ,default=Value('Outstanding'), output_field=CharField())
        , informationsecurity_status=Case(
            When(informationsecurity__gt=twelve_months_ago
                , then=Value('Received'))
            , When(informationsecurity__lt=twelve_months_ago
                , then=Value('Expired'))
                ,default=Value('Outstanding'), output_field=CharField())
        , safe_status=Case(
            When(safe__gt=three_years_ago
                , then=Value('Received'))
            , When(safe__lt=three_years_ago,then=Value('Expired')), output_field=CharField())
    ).order_by("firstname", "lastname")

    context = {'projectnumber': projectnumber
        , 'project_user_docs': project_user_docs}

    return render(request, 'Prism/userdocs.html', context)

@login_required
@permission_required(["Prism.view_tbluser"], raise_exception=True)
def users(request):
    query = request.GET

    filter_query = {}
    advanced_filter_query = {}
    filter_list = []

    if query is not None and query != '':
        for key in query:
            value = query.get(key)
            if value != '':
                if key == 'q':
                    filter_query['firstname__icontains'] = value
                    filter_query['lastname__icontains'] = value
                    filter_list.append(f"First or Last Name contains '{value}'")
                if key == 'status_id':
                    advanced_filter_query['status__statusid__iexact'] = value
                    filter_list.append(f"Status is '{Tlkuserstatus.objects.get(statusid=value)}'")
                if key == 'username':
                    advanced_filter_query['username__icontains'] = value
                    filter_list.append(f"Username contains '{value}'")
                if key == 'email':
                    advanced_filter_query['email__icontains'] = value
                    filter_list.append(f"Email contains'{value}'")
                if key == 'organisation':
                    advanced_filter_query['organisation__icontains'] = value
                    filter_list.append(f"Organisation contains '{value}'")

    users = Tbluser.objects.filter(
            Q(**filter_query, _connector=Q.OR)
            , Q(**advanced_filter_query, _connector=Q.AND)
            , validto__isnull=True
        ).values(
            "userid"
            , "usernumber"
            , "status__statusdescription"
            , "firstname"
            , "lastname"
            , "email"
            , "username"
            , "organisation"
        ).order_by("lastname")

    filter_string = ", ".join(filter_list)
    user_search_form = UserSearchForm()

    return render(request, 'Prism/users.html', {'users': users
                                                   ,'user_form': user_search_form
                                                   ,'searchterms': filter_string})

@login_required
@permission_required(["Prism.view_tbluser", "Prism.add_tbluser", "Prism.change_tbluser"
                      , "Prism.view_tblproject", "Prism.view_tbluserproject", "Prism.add_tbluserproject", "Prism.change_tbluserproject"
                      , "Prism.view_tblusernotes", "Prism.add_tblusernotes", "Prism.change_tblusernotes"], raise_exception=True)
def user(request, usernumber):
    # Build forms
    
    ## USER ##
    user = Tbluser.objects.filter(
        validto__isnull=True
        , usernumber=usernumber
    ).values(
    ).get()         # get() with no arguments will raise an exception if the queryset doesn't contain exactly one item

    ## PROJECT MEMBERSHIP ##
    # Using OuterRef & Subquery to perform a lookup against Tblproject on Tbluserproject's projectnumber and add it to the model with annotate 
    projectnames = Tblproject.objects.filter(
        validto__isnull=True
        ,projectnumber=OuterRef("projectnumber")
    ).values("projectname")

    user_project = Tbluserproject.objects.filter(
        validto__isnull=True
        , usernumber=usernumber
    ).values(
    ).annotate(projectname = Subquery(projectnames)
    ).order_by("projectnumber")

    ## USER NOTES ##
    query = request.GET.get("search_notes")
    filter_query = {}
    if query is not None and query != '':
        filter_query['unote__icontains'] = query
    
    user_notes = Tblusernotes.objects.filter(
        Q(**filter_query, _connector=Q.OR)
        , usernumber=usernumber
    ).values(
    ).order_by("-created")

    paginator = Paginator(user_notes, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ## CREATE FORMS ##
    user_form = UserForm(initial=user, prefix='user')
    user_project_form = UserProjectForm(prefix='user_project')
    user_project_form.initial['usernumber'] = usernumber
    u_notes_form = UserNotesForm(prefix='u_note')
    
    context={'user': user
            , 'user_form': user_form
            , 'user_project': user_project
            , 'user_project_form': user_project_form
            , 'notes':page_obj
            , 'notes_filter' : query
            , 'new_note': u_notes_form
             }

    if request.method == 'POST':
        if 'user-userid' in request.POST:
            user_form = UserForm(request.POST, prefix='user')
            if user_form.is_valid():
                userid = user_form.cleaned_data['userid']
                insert = Tbluser(
                    usernumber = usernumber
                    ,status = user_form.cleaned_data['status_id']
                    ,firstname = user_form.cleaned_data['firstname']
                    ,lastname = user_form.cleaned_data['lastname']
                    ,email = user_form.cleaned_data['email']
                    ,phone = user_form.cleaned_data['phone']
                    ,username = user_form.cleaned_data['username']
                    ,organisation = user_form.cleaned_data['organisation']
                    ,startdate = user_form.cleaned_data['startdate']
                    ,enddate = user_form.cleaned_data['enddate']
                    ,laseragreement = user_form.cleaned_data['laseragreement']
                    ,dataprotection = user_form.cleaned_data['dataprotection']
                    ,informationsecurity = user_form.cleaned_data['informationsecurity']
                    ,safe = user_form.cleaned_data['safe']
                    ,priviledged = user_form.cleaned_data['priviledged']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                
                # Fetch existing user record
                existing_user = Tbluser.objects.filter(
                    validto__isnull=True
                    , usernumber=usernumber
                ).values(
                ).get() 

                # Only save record if fields have changed
                if recordchanged(existing_record=existing_user, form_set=insert):
                    insert.save(force_insert=True)

                    delete = Tbluser(
                        userid = userid
                        ,validto = timezone.now()
                    )
                    delete.save(update_fields=["validto"])
                
                    messages.success(request, 'User updated successfully.')
                return HttpResponseRedirect(f"/user/{usernumber}")
            else:
                context['user_form']=user_form

        elif 'user_project-projectnumber' in request.POST:
            user_project_form = UserProjectForm(request.POST, prefix='user_project')

            if user_project_form.is_valid():
                insert_user_project = Tbluserproject(
                    usernumber = usernumber
                    ,projectnumber = user_project_form.cleaned_data['projectnumber'].projectnumber
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                insert_user_project.save(force_insert=True)
                messages.success(request, 'User Project membership added successfully.')
                return HttpResponseRedirect(f"/user/{usernumber}")
            else:
                context['user_project_form']=user_project_form

        elif 'u_note-unote' in request.POST:
            u_notes_form = UserNotesForm(request.POST, prefix='u_note')
            if u_notes_form.is_valid():
                insert_note = Tblusernotes(
                    usernumber = usernumber
                    ,unote = u_notes_form.cleaned_data['unote']
                    ,created = timezone.now()
                    ,createdby = request.user
                )
                insert_note.save(force_insert=True)
                messages.success(request, 'User note added successfully.')
                return HttpResponseRedirect(f"/user/{usernumber}")
            else:
                context['new_note']=u_notes_form

        return render(request, 'Prism/user.html', context)

    if request.method == 'GET':
        return render(request, 'Prism/user.html', context)

@login_required
@permission_required(["Prism.add_tbluser"], raise_exception=True)
def usercreate(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():

            # Get latest UserNumber from database model and iterate up by one for new UserNumber
            max_usernumber = Tbluser.objects.filter(
                validto__isnull=True
            ).aggregate(Max("usernumber"))
            new_usernumber = max_usernumber['usernumber__max'] + 1
            
            insert = Tbluser(
                usernumber = new_usernumber
                ,status = user_form.cleaned_data['status_id']
                ,firstname = user_form.cleaned_data['firstname']
                ,lastname = user_form.cleaned_data['lastname']
                ,email = user_form.cleaned_data['email']
                ,phone = user_form.cleaned_data['phone']
                ,username = user_form.cleaned_data['username']
                ,organisation = user_form.cleaned_data['organisation']
                ,startdate = user_form.cleaned_data['startdate']
                ,enddate = user_form.cleaned_data['enddate']
                ,laseragreement = user_form.cleaned_data['laseragreement']
                ,dataprotection = user_form.cleaned_data['dataprotection']
                ,informationsecurity = user_form.cleaned_data['informationsecurity']
                ,safe = user_form.cleaned_data['safe']
                ,validfrom = timezone.now()
                ,validto = None
                ,createdby = request.user
                )
            
            # Check if record already exists in database with matching values
            duplicate_qs = Tbluser.objects.none()
            if insert.email:
                duplicate_qs = duplicate_qs | Tbluser.objects.filter(validto__isnull=True
                                                                    ,email__iexact=insert.email)
            if insert.username:
                duplicate_qs = duplicate_qs | Tbluser.objects.filter(validto__isnull=True
                                                                    ,email__iexact=insert.username)
            if insert.firstname and insert.lastname:
                duplicate_qs = duplicate_qs | Tbluser.objects.filter(validto__isnull=True
                                                                    ,firstname__iexact=insert.firstname
                                                                    ,lastname__iexact=insert.lastname
                                                                    )
                duplicate_qs = duplicate_qs | Tbluser.objects.filter(validto__isnull=True
                                                                    ,firstname__iexact=insert.lastname
                                                                    ,lastname__iexact=insert.firstname
                                                                    )
            duplicate_qs = duplicate_qs.distinct()
            # This is a hidden input in the User form template, only rendered if ask_confirm=True. user_confirmed==False if not present
            user_confirmed = request.POST.get("confirm_duplicate") == "1"

            # Render a confirmation prompt if a potential duplicate exists
            if duplicate_qs.exists() and not user_confirmed:
                return render(request, 'Prism/user_new.html', {'user_form':user_form
                                                               ,'possible_duplicates':duplicate_qs
                                                               ,'ask_confirm': True})   

            # If no potential duplicate or submission confirmed, submit
            insert.save(force_insert=True)

            return HttpResponseRedirect(f"/user/{new_usernumber}")
        else:
            return render(request, 'Prism/user_new.html', {'user_form':user_form})   

    if request.method == 'GET':
        user_form = UserForm()
        return render(request, 'Prism/user_new.html', {'user_form':user_form})

@login_required
@permission_required(["Prism.change_tbluserproject"], raise_exception=True)
def userproject_remove(request, userprojectid):
    update_record=Tbluserproject.objects.filter(
        userprojectid=userprojectid
    ).values()
    update_record.update(validto = timezone.now())
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@permission_required(["Prism.change_tblprojectkristal"], raise_exception=True)
def projectkristal_remove(request, projectkristalid):
    update_record=Tblprojectkristal.objects.filter(
        projectkristalid=projectkristalid
    ).values()
    update_record.update(validto = timezone.now())
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@permission_required(["Prism.view_tblkristal"], raise_exception=True)
def grants(request):
    query = request.GET

    filter_query = {}
    advanced_filter_query = {}
    filter_list = []

    if query is not None and query != '':
        for key in query:
            value = query.get(key)
            if value != '':
                if key == 'q':
                    filter_query['kristalname__icontains'] = value
                    filter_query['kristalref__icontains'] = value
                    filter_list.append(f"Kristal Name or Reference contains '{value}'")
                if key == 'grantstageid_id':
                    advanced_filter_query['grantstageid__grantstageid__iexact'] = value
                    filter_list.append(f"Grant Stage is '{tlkGrantStage.objects.get(grantstageid=value)}'")
                if key == 'faculty_id':
                    advanced_filter_query['faculty__facultyid__iexact'] = value
                    filter_list.append(f"Faculty is '{Tlkfaculty.objects.get(facultyid=value)}'")
                if key == 'location_id':
                    advanced_filter_query['location__locationid__iexact'] = value
                    filter_list.append(f"Location is '{Tlklocation.objects.get(locationid=value)}'")
                if key == 'laser':
                    advanced_filter_query['laser__iexact'] = True
                    filter_list.append(f"LASER = {True}")
                if key == 'dsdp':
                    advanced_filter_query['dsdp__iexact'] = True
                    filter_list.append(f"DSDP = {True}")
                if key == 'ridm':
                    advanced_filter_query['ridm__iexact'] = True
                    filter_list.append(f"RIDM = {True}")
                if key == 'community':
                    advanced_filter_query['community__iexact'] = True
                    filter_list.append(f"Community = {True}")
                
    grants = Tblkristal.objects.filter(
            Q(**filter_query, _connector=Q.OR)
            , Q(**advanced_filter_query, _connector=Q.AND)
            , validto__isnull=True
        ).values(
            "kristalid"
            , "kristalnumber"
            , "kristalref"
            , "kristalname"
            , "grantstageid__grantstagedescription"
            , "location__locationdescription"
            , "faculty__facultydescription"
        ).order_by("kristalref")

    filter_string = ", ".join(filter_list)
    grant_search_form = GrantSearchForm()

    return render(request, 'Prism/grants.html', {'grants': grants
                                                   ,'grant_form': grant_search_form
                                                   ,'searchterms': filter_string})

@login_required
@permission_required(["Prism.view_tblkristal", "Prism.add_tblkristal", "Prism.change_tblkristal"
                      , "Prism.view_tblproject", "Prism.view_tblprojectkristal", "Prism.add_tblprojectkristal", "Prism.change_tblprojectkristal"
                      , "Prism.view_tblkristalnotes", "Prism.add_tblkristalnotes", "Prism.change_tblkristalnotes"], raise_exception=True)
def grant(request, kristalnumber):
    # Build forms
    
    ## GRANT ##
    grant = Tblkristal.objects.filter(
        validto__isnull=True
        , kristalnumber=kristalnumber
    ).values(
    ).get()         # get() with no arguments will raise an exception if the queryset doesn't contain exactly one item

    # Using OuterRef & Subquery to perform a lookup against Tblproject on Tblprojectkristal's projectnumber and add it to the model with annotate 
    projectnames = Tblproject.objects.filter(
        validto__isnull=True
        ,projectnumber=OuterRef("projectnumber")
    ).values("projectname")
    projectstages = Tblproject.objects.filter(
        validto__isnull=True
        ,projectnumber=OuterRef("projectnumber")
    ).values("stage__pstagedescription")
    project_laser = Tblproject.objects.filter(
        validto__isnull=True
        ,projectnumber=OuterRef("projectnumber")
    ).values("laser")
    project_dsdp = Tblproject.objects.filter(
        validto__isnull=True
        ,projectnumber=OuterRef("projectnumber")
    ).values("internship")

    grant_project = Tblprojectkristal.objects.filter(
        validto__isnull=True
        , kristalnumber=kristalnumber
    ).values(
    ).annotate(projectname = Subquery(projectnames)
               , stage = Subquery(projectstages)
               , laser = Subquery(project_laser)
               , dsdp = Subquery(project_dsdp)
    ).order_by("projectnumber")

    ## GRANT NOTES ##
    query = request.GET.get("search_notes")
    filter_query = {}
    if query is not None and query != '':
        filter_query['kristalnote__icontains'] = query
    
    grant_notes = Tblkristalnotes.objects.filter(
        Q(**filter_query, _connector=Q.OR)
        , kristalnumber=kristalnumber
    ).values(
    ).order_by("-created")

    paginator = Paginator(grant_notes, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ## PORTFOLIO PLUS ##
    portfolio_plus = tblPortfolioPlus.objects.filter(
        validto__isnull=True
        , grant=grant['kristalref']
    ).values(
    ).get()         # get() with no arguments will raise an exception if the queryset doesn't contain exactly one item

    ## CREATE FORMS ##
    grant_form = KristalForm(initial=grant, prefix='grant')
    grant_project_form = ProjectKristalForm(prefix='grant_project')
    grant_project_form.initial['kristalnumber'] = kristalnumber
    grant_notes_form = GrantNotesForm(prefix='grant_note')
    
    ## DATA VALIDATION ##
    # Populated on GET Request
    custom_errors = []

    context={'grant': grant
            , 'grant_form': grant_form
            , 'portfolio_plus': portfolio_plus
            , 'grant_project': grant_project
            , 'grant_project_form': grant_project_form
            , 'notes':page_obj
            , 'notes_filter' : query
            , 'new_note': grant_notes_form
            , 'custom_errors': custom_errors
             }

    if request.method == 'POST':
        if 'grant-kristalid' in request.POST:
            grant_form = KristalForm(request.POST, prefix='grant')
            if grant_form.is_valid():
                kristalid = grant_form.cleaned_data['kristalid']
                pi = None
                if grant_form.cleaned_data['pi'] != None:
                    pi = grant_form.cleaned_data['pi'].usernumber
                insert = Tblkristal(
                    kristalnumber = kristalnumber
                    ,kristalref = grant_form.cleaned_data['kristalref']
                    ,kristalname = grant_form.cleaned_data['kristalname']
                    ,grantstageid = grant_form.cleaned_data['grantstageid_id']
                    ,pi = pi
                    ,location = grant_form.cleaned_data['location_id']
                    ,faculty = grant_form.cleaned_data['faculty_id']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                    ,laser = grant_form.cleaned_data['laser']
                    ,dsdp = grant_form.cleaned_data['dsdp']
                    ,ridm = grant_form.cleaned_data['ridm']
                    ,community = grant_form.cleaned_data['community']
                )
                
                # Fetch existing user record
                existing_grant = Tblkristal.objects.filter(
                    validto__isnull=True
                    , kristalnumber=kristalnumber
                ).values(
                ).get() 

                # Only save record if fields have changed
                with transaction.atomic():
                    if recordchanged(existing_record=existing_grant, form_set=insert):
                        delete = Tblkristal(
                            kristalid = kristalid
                            ,validto = timezone.now()
                        )
                        delete.save(update_fields=["validto"])
                        insert.save(force_insert=True)                   
                        messages.success(request, 'Grant updated successfully.')
                    return HttpResponseRedirect(f"/grant/{kristalnumber}")
            else:
                context['grant_form']=grant_form

        elif 'grant_project-kristalnumber' in request.POST:
            grant_project_form = ProjectKristalForm(request.POST, prefix='grant_project')
            if grant_project_form.is_valid():
                insert_grant_project = Tblprojectkristal(
                    kristalnumber = kristalnumber
                    ,projectnumber = grant_project_form.cleaned_data['projectnumber'].projectnumber
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                )
                insert_grant_project.save(force_insert=True)
                messages.success(request, 'Grant Project membership added successfully.')
                return HttpResponseRedirect(f"/grant/{kristalnumber}")
            else:
                context['grant_project_form']=grant_project_form

        elif 'grant_note-kristalnote' in request.POST:
            grant_notes_form = GrantNotesForm(request.POST, prefix='grant_note')
            if grant_notes_form.is_valid():
                insert_note = Tblkristalnotes(
                    kristalnumber = kristalnumber
                    ,kristalnote = grant_notes_form.cleaned_data['kristalnote']
                    ,created = timezone.now()
                    ,createdby = request.user
                )
                insert_note.save(force_insert=True)
                messages.success(request, 'Grant note added successfully.')
                return HttpResponseRedirect(f"/grant/{kristalnumber}")
            else:
                context['new_note']=grant_notes_form

        return render(request, 'Prism/grant.html', context)

    if request.method == 'GET':

        ## DATA VALIDATION ##
        # For information purposes only. 
        # Validation across/between forms or where errors not sufficient to prevent form submission.

        # Do Grant LASER/DSDP status align with any projects on Grant?
        if grant_project:
            p_laser = []
            p_dsdp = []
            for project in grant_project:
                if project['laser']: 
                    p_laser.append(project['projectnumber'])
                if project['dsdp']:
                    p_dsdp.append(project['projectnumber'])

            if grant['laser'] and not p_laser:
                custom_errors.append("Grant has no LASER project(s) but is LASER == True")
            if not grant['laser'] and p_laser:
                custom_errors.append(f"Grant has LASER project(s) but is LASER == False {p_laser}")
            if grant['dsdp'] and not p_dsdp:
                custom_errors.append("Grant has no DSDP project(s) but is DSDP == True")
            if not grant['dsdp'] and p_dsdp:
                custom_errors.append(f"Grant has DSDP project(s) but is DSDP == False {p_dsdp}")
        else:
            if grant['laser']:
                custom_errors.append("Grant has no LASER project(s) but is LASER == True")
            if grant['dsdp']:
                custom_errors.append("Grant has no DSDP project(s) but is DSDP == True")

        return render(request, 'Prism/grant.html', context)

@login_required
@permission_required(["Prism.add_tblkristal"], raise_exception=True)
def grantcreate(request):
    if request.method == "POST":
        kristal_form = KristalForm(request.POST)
        if kristal_form.is_valid():
            # Check if Kristal Ref alrady exists in Tblkristal
            if not Tblkristal.objects.filter(validto__isnull=True, kristalref = kristal_form.cleaned_data['kristalref']).exists():
                # If it doesn't insert new record to Tblkristal
                # Get latest KristalNumber from database model and iterate up by one for new KristalNumber
                max_kristalnumber = Tblkristal.objects.filter(
                    validto__isnull=True
                ).aggregate(Max("kristalnumber"))
                new_kristalnumber = max_kristalnumber['kristalnumber__max'] + 1

                pi = None
                if kristal_form.cleaned_data['pi'] != None:
                    pi = kristal_form.cleaned_data['pi'].usernumber

                insert_new_kristal = Tblkristal(
                    kristalnumber = new_kristalnumber
                    ,kristalref = kristal_form.cleaned_data['kristalref']
                    ,kristalname = kristal_form.cleaned_data['kristalname']
                    ,grantstageid = kristal_form.cleaned_data['grantstageid_id']
                    ,pi = pi
                    ,location = kristal_form.cleaned_data['location_id']
                    ,faculty = kristal_form.cleaned_data['faculty_id']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,createdby = request.user
                    ,laser = kristal_form.cleaned_data['laser']
                    ,dsdp = kristal_form.cleaned_data['dsdp']
                    ,ridm = kristal_form.cleaned_data['ridm']
                    ,community = kristal_form.cleaned_data['community']
                )

                insert_new_kristal.save(force_insert=True)

                return HttpResponseRedirect(f"/grant/{new_kristalnumber}")

            else:
                kristal_form.add_error(None, "Grant already exists in Prism")
                return render(request, 'Prism/grant_new.html', {'kristal_form':kristal_form})

        else:
            return render(request, 'Prism/grant_new.html', {'kristal_form':kristal_form})

    if request.method == 'GET':
        kristal_form = KristalForm()
        return render(request, 'Prism/grant_new.html', {'kristal_form':kristal_form})

@login_required
@permission_required(["Prism.view_tblkristal"], raise_exception=True)
def grants_no_routing(request):

    null_filter_query = {"laser__isnull": True
                             , "dsdp__isnull": True
                             , "ridm__isnull": True
                             , "community__isnull": True}
    false_filter_query = {"laser": False
                             , "dsdp": False
                             , "ridm": False
                             , "community": False}

    grants = Tblkristal.objects.filter(
            Q(**null_filter_query, _connector=Q.AND)
            | Q(**false_filter_query, _connector=Q.AND)
            , validto__isnull=True
        ).values(
            "kristalid"
            , "kristalnumber"
            , "kristalref"
            , "kristalname"
            , "grantstageid__grantstagedescription"
            , "location__locationdescription"
            , "faculty__facultydescription"
        ).order_by("validfrom", "kristalref")

    filter_string = "No Routing"
    grant_search_form = GrantSearchForm()

    return render(request, 'Prism/grants.html', {'grants': grants
                                                   ,'grant_form': grant_search_form
                                                   ,'searchterms': filter_string})

@login_required
@permission_required(["Prism.view_tbldsas", "Prism.view_tbldsadataowners"], raise_exception=True)
def dsas (request):
    query = request.GET

    filter_query = {}
    advanced_filter_query = {}
    filter_list = []

    if query is not None and query != '':
        for key in query:
            value = query.get(key)
            if value != '':
                if key == 'q':
                    filter_query['dsaname__icontains'] = value
                    filter_list.append(f"DSA File Name contains '{value}'")
                if key == 'dataowner_id':
                    advanced_filter_query['dataowner__doid__iexact'] = value
                    filter_list.append(f"Data Owner is '{Tbldsadataowners.objects.get(doid=value)}'")
                
                if key == 'project':
                    documentlist = Tbldsasprojects.objects.filter(validto__isnull=True, project=value).values_list("documentid")
                    advanced_filter_query ['documentid__in'] = documentlist
                    filter_list.append(f"Project Number = '{value}'")
                
                if key == 'dspt':
                    advanced_filter_query['dspt__iexact'] = True
                    filter_list.append(f"NHS DSPT = {True}")
                if key == 'iso27001':
                    advanced_filter_query['iso27001__iexact'] = True
                    filter_list.append(f"ISO27001 = {True}")
                if key == 'requiresencryption':
                    advanced_filter_query['requiresencryption__iexact'] = True
                    filter_list.append(f"Requires Encryption = {True}")
                if key == 'noremoteaccess':
                    advanced_filter_query['noremoteaccess__iexact'] = True
                    filter_list.append(f"No Remote Access = {True}")
                
    dsas = Tbldsas.objects.filter(
            Q(**filter_query, _connector=Q.OR)
            , Q(**advanced_filter_query, _connector=Q.AND)
            , validto__isnull=True
        ).values(
            "documentid"
            , "dataowner__dataownername"
            , "dsaname"
            , "startdate"
            , "expirydate"
            , "datadestructiondate"
            , "dspt"
            , "iso27001"
            , "requiresencryption"
            , "noremoteaccess"
        ).annotate(is_expired=Case(When(expirydate__lt=timezone.now(), then=True),default=False,output_field=BooleanField())
        ).order_by("dataowner__dataownername")

    filter_string = ", ".join(filter_list)
    dsa_search_form = DsaSearchForm()

    context = {'dsas': dsas
        ,'dsa_form': dsa_search_form
        ,'searchterms': filter_string
        }
    
    return render(request, 'Prism/dsas.html', context)

@login_required
@permission_required(["Prism.view_tbldsas", "Prism.add_tbldsas", "Prism.change_tbldsas"
                      , "Prism.view_tblproject", "Prism.view_tbldsasprojects", "Prism.add_tbldsasprojects", "Prism.change_tbldsasprojects"
                      , "Prism.view_tbldsanotes", "Prism.add_tbldsanotes", "Prism.change_tbldsanotes"], raise_exception=True)
def dsa(request, documentid):
    # Build forms
    
    ## DSA ##
    dsa = Tbldsas.objects.filter(
        validto__isnull=True
        , documentid=documentid
    ).values(
    ).get()         # get() with no arguments will raise an exception if the queryset doesn't contain exactly one item

    ## PROJECTS ##
    # Using OuterRef & Subquery to perform a lookup against Tblproject on Tbldsasprojects' projectnumber and add it to the model with annotate 
    projectnames = Tblproject.objects.filter(
        validto__isnull=True
        ,projectnumber=OuterRef("project")
    ).values("projectname")

    dsa_project = Tbldsasprojects.objects.filter(
        validto__isnull=True
        , documentid=documentid
    ).values(
    ).annotate(projectname = Subquery(projectnames)
    ).order_by("project")

    ## DSA NOTES ##
    query = request.GET.get("search_notes")
    filter_query = {}
    if query is not None and query != '':
        filter_query['note__icontains'] = query
    
    dsa_notes = Tbldsanotes.objects.filter(
        Q(**filter_query, _connector=Q.OR)
        , dsa=documentid
    ).values(
    ).order_by("-created")

    paginator = Paginator(dsa_notes, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ## CREATE FORMS ##
    dsa_form = DsaForm(initial=dsa, prefix="dsa")
    dsa_project_form = ProjectDsaForm(prefix='dsa_project')
    dsa_project_form.initial['documentid'] = documentid
    dsa_notes_form = DsaNotesForm(prefix='dsa_note')

    ## DATA VALIDATION ##
    # Populated on GET Request
    custom_errors = []

    context = {'dsa': dsa
            , 'dsa_form': dsa_form
            , 'dsa_project': dsa_project
            , 'dsa_project_form': dsa_project_form
            , 'notes':page_obj
            , 'notes_filter' : query
            , 'new_note': dsa_notes_form
            , 'custom_errors': custom_errors
            }

    if request.method == 'POST':
        if 'dsa-dsaid' in request.POST:
            dsa_form = DsaForm(request.POST, prefix='dsa')
            if dsa_form.is_valid():
                dsaid = dsa_form.cleaned_data['dsaid']
                insert = Tbldsas(
                    documentid = documentid
                    ,dataowner = dsa_form.cleaned_data['dataowner_id']
                    ,dsaname = dsa_form.cleaned_data['dsaname']
                    ,dsafileloc = dsa_form.cleaned_data['dsafileloc']
                    ,startdate = dsa_form.cleaned_data['startdate']
                    ,expirydate = dsa_form.cleaned_data['expirydate']
                    ,datadestructiondate = dsa_form.cleaned_data['datadestructiondate']
                    ,agreementowneremail = dsa_form.cleaned_data['agreementowneremail']
                    ,dspt = dsa_form.cleaned_data['dspt']
                    ,iso27001 = dsa_form.cleaned_data['iso27001']
                    ,requiresencryption = dsa_form.cleaned_data['requiresencryption']
                    ,noremoteaccess = dsa_form.cleaned_data['noremoteaccess']
                    ,validfrom = timezone.now()
                    ,validto = None
                    ,deprecated = False
                )
                
                # Fetch existing user record
                existing_dsa = Tbldsas.objects.filter(
                    validto__isnull=True
                    , documentid=documentid
                ).values(
                ).get() 

                # Only save record if fields have changed
                if recordchanged(existing_record=existing_dsa, form_set=insert):
                    insert.save(force_insert=True)

                    delete = Tbldsas(
                        dsaid = dsaid
                        ,validto = timezone.now()
                    )
                    delete.save(update_fields=["validto"])
                
                    messages.success(request, 'DSA updated successfully.')
                return HttpResponseRedirect(f"/dsa/{documentid}")
            else:
                context['dsa_form']=dsa_form
            
        elif 'dsa_project-documentid' in request.POST:
            dsa_project_form = ProjectDsaForm(request.POST, prefix='dsa_project')
            if dsa_project_form.is_valid():
                insert_dsa_project = Tbldsasprojects(
                    documentid = documentid
                    ,project = dsa_project_form.cleaned_data['project'].projectnumber
                    ,validfrom = timezone.now()
                    ,validto = None
                )
                insert_dsa_project.save(force_insert=True)
                messages.success(request, 'DSA Project membership added successfully.')
                return HttpResponseRedirect(f"/dsa/{documentid}")
            else:
                context['dsa_project_form']=dsa_project_form
        
        elif 'dsa_note-note' in request.POST:
            dsa_notes_form = DsaNotesForm(request.POST, prefix='dsa_note')
            if dsa_notes_form.is_valid():
                insert_note = Tbldsanotes(
                    dsa = documentid
                    ,note = dsa_notes_form.cleaned_data['note']
                    ,created = timezone.now()
                    ,createdby = request.user
                )
                insert_note.save(force_insert=True)
                messages.success(request, 'DSA note added successfully.')
                return HttpResponseRedirect(f"/dsa/{documentid}")
            else:
                context['new_note']=dsa_notes_form

        return render(request, "Prism/dsa.html", context)

    if request.method == 'GET':
        ## DATA VALIDATION ##
        # For information purposes only. 
        # Validation across/between forms or where errors not sufficient to prevent form submission.

        # Are end dates present?
        if not dsa['expirydate'] :
            custom_errors.append("DSA is missing Expiry Date")
        if not dsa['datadestructiondate']:
            custom_errors.append("DSA is missing Data Destruction Date")
        # Is the DSA expired?
        if dsa['expirydate'] and dsa['expirydate'] < timezone.now():
            custom_errors.append("DSA has expired; is there an updated version available?")
        # Has data destruction date passed?
        if dsa['datadestructiondate'] and dsa['datadestructiondate'] < timezone.now():
            custom_errors.append("Data destruction date has passed; has the data been destroyed?")

        return render(request, "Prism/dsa.html", context)

@login_required
@permission_required("Prism.add_tbldsas", raise_exception=True)
def dsacreate(request):
    if request.method == "POST":
        dsa_form = DsaForm(request.POST)
        if dsa_form.is_valid():

            # Get latest documentid from database model and iterate up by one for new documentid
            max_documentid = Tbldsas.objects.filter(
                validto__isnull=True
            ).aggregate(Max("documentid"))
            new_documentid = max_documentid['documentid__max'] + 1
            
            insert = Tbldsas(
                documentid = new_documentid
                ,dataowner = dsa_form.cleaned_data['dataowner_id']
                ,dsaname = dsa_form.cleaned_data['dsaname']
                ,dsafileloc = dsa_form.cleaned_data['dsafileloc']
                ,startdate = dsa_form.cleaned_data['startdate']
                ,expirydate = dsa_form.cleaned_data['expirydate']
                ,datadestructiondate = dsa_form.cleaned_data['datadestructiondate']
                ,agreementowneremail = dsa_form.cleaned_data['agreementowneremail']
                ,dspt = dsa_form.cleaned_data['dspt']
                ,iso27001 = dsa_form.cleaned_data['iso27001']
                ,requiresencryption = dsa_form.cleaned_data['requiresencryption']
                ,noremoteaccess = dsa_form.cleaned_data['noremoteaccess']
                ,validfrom = timezone.now()
                ,validto = None
                ,deprecated = False
            )
            insert.save(force_insert=True)

            return HttpResponseRedirect(f"/dsa/{new_documentid}")
        else:
            return render(request, 'Prism/dsa_new.html', {'dsa_form':dsa_form})   

    if request.method == 'GET':
        dsa_form = DsaForm()
        return render(request, 'Prism/dsa_new.html', {'dsa_form':dsa_form})

@login_required
@permission_required(["Prism.change_tbldsasprojects"], raise_exception=True)
def projectdsa_remove(request, dpid):
    update_record=Tbldsasprojects.objects.filter(
        dpid=dpid
    ).values()
    update_record.update(validto = timezone.now())
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@permission_required("Prism.add_tbldsadataowners", raise_exception=True)
def dataownercreate(request):
    if request.method == "POST":
        data_owner_form = DataOwnerCreateForm(request.POST)
        if data_owner_form.is_valid():
            
            insert = Tbldsadataowners(
                dataownername = data_owner_form.cleaned_data['dataownername']
                ,dataowneremail = data_owner_form.cleaned_data['dataowneremail']
            )

            # Check if record already exists in database with matching values
            duplicate_qs = Tbldsadataowners.objects.none()
            if insert.dataownername:
                duplicate_qs = duplicate_qs | Tbldsadataowners.objects.filter(dataownername__icontains=insert.dataownername)
            if insert.dataowneremail:
                duplicate_qs = duplicate_qs | Tbldsadataowners.objects.filter(dataowneremail__icontains=insert.dataowneremail)

            duplicate_qs = duplicate_qs.distinct().order_by("dataownername")
            # This is a hidden input in the Data Owner Create template, only rendered if ask_confirm=True. data_owner_confirmed==False if not present
            data_owner_confirmed = request.POST.get("confirm_duplicate") == "1"

            # Render a confirmation prompt if a potential duplicate exists
            if duplicate_qs.exists() and not data_owner_confirmed:
                return render(request, 'Prism/data_owner_new.html', {'data_owner_form':data_owner_form
                                                               ,'possible_duplicates':duplicate_qs
                                                               ,'ask_confirm': True})   
            
            insert.save(force_insert=True)

            return HttpResponseRedirect("/dsas")
        else:
            return render(request, 'Prism/data_owner_new.html', {'data_owner_form':data_owner_form})   

    if request.method == 'GET':
        data_owner_form = DataOwnerCreateForm()
        return render(request, 'Prism/data_owner_new.html', {'data_owner_form':data_owner_form})   

@login_required
@permission_required(["Prism.view_tbltransferrequest", "Prism.view_tbluser"], raise_exception=True)
def transferrequests(request):
    query = request.GET

    advanced_filter_query = {}
    filter_list = []

    if query is not None and query != '':
        for key in query:
            value = query.get(key)
            if value != '':
                if key == 'projectnumber':
                    advanced_filter_query['projectnumber__iexact'] = value
                    filter_list.append(f"Project is '{value}'")
                if key == 'requesttype':
                    advanced_filter_query['requesttype__exact'] = value
                    filter_list.append(f"Request Type is '{Tlktransferrequesttypes.objects.get(requesttypeid=value)}'")
                if key == 'requestedby':
                    advanced_filter_query['requestedby__iexact'] = value
                    filter_list.append(f"Requested By '{Tbluser.objects.get(usernumber=value, validto__isnull=True)}'")
                if key == 'reviewedby':
                    advanced_filter_query['reviewedby__iexact'] = value
                    filter_list.append(f"Reviewed By '{Tbluser.objects.get(usernumber=value, validto__isnull=True)}'")
                if key == 'reviewdate':
                    advanced_filter_query['reviewdate__date__iexact'] = value
                    filter_list.append(f"Review Date is '{value}'")
                
    transfers = Tbltransferrequest.objects.filter(
            Q(**advanced_filter_query, _connector=Q.AND)
        ).values(
            "requestid"
            , "projectnumber"
            , "requesttype"
            , "requesttype__requesttypelabel"
            , "requestedby"
            , "reviewedby"
            , "reviewdate"
            , "transfermethod"
            , "transfermethod__methodlabel"
            , "transferfrom"
            , "transferto"
            , "dsareviewed"
        ).order_by("-requestid")

    users = Tbluser.objects.filter(
            validto__isnull=True
            ).values()
    
    df = pd.DataFrame(users)

    for transfer in transfers:
        if transfer['requestedby'] is not None:
            requestedby_index = df.index[df['usernumber'] == transfer['requestedby']].tolist()
            requestedby_name = f"{df.at[requestedby_index[0],'firstname']} {df.at[requestedby_index[0],'lastname']}"
            transfer.update(requestedby=requestedby_name)
        if transfer['reviewedby'] is not None:
            reviewedby_index = df.index[df['usernumber'] == transfer['reviewedby']].tolist()
            reviewedby_name = f"{df.at[reviewedby_index[0],'firstname']} {df.at[reviewedby_index[0],'lastname']}"
            transfer.update(reviewedby=reviewedby_name)

    paginator = Paginator(transfers, 25)  # Show 5 posts per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    get_copy = request.GET.copy()
    if 'page' in get_copy:
        get_copy.pop('page')

    filter_string = ", ".join(filter_list)
    transfer_search_form = TransferSearchForm()

    return render(request, 'Prism/transfers.html', {'transfers': page_obj
                                                    ,'transfer_search_form': transfer_search_form
                                                    ,'searchterms': filter_string
                                                    ,'query': get_copy.urlencode()
                                                    })

@login_required
@permission_required(["Prism.view_tbluser", "Prism.view_tbldsas"
                      , "Prism.view_tbltransferrequest", "Prism.view_tbltransferfile", "Prism.view_tbltransferfileasset"], raise_exception=True)
def transferrequest(request, requestid):
    requestedby_firstname = Tbluser.objects.filter(
        validto__isnull=True
        ,usernumber=OuterRef("requestedby")
    ).values("firstname")

    requestedby_lastname = Tbluser.objects.filter(
        validto__isnull=True
        ,usernumber=OuterRef("requestedby")
    ).values("lastname")

    reviewedby_firstname = Tbluser.objects.filter(
        validto__isnull=True
        ,usernumber=OuterRef("reviewedby")
    ).values("firstname")

    reviewedby_lastname = Tbluser.objects.filter(
        validto__isnull=True
        ,usernumber=OuterRef("reviewedby")
    ).values("lastname")

    dsa_reviewed = Tbldsas.objects.filter(
        validto__isnull=True
        ,documentid=OuterRef("dsareviewed")
    ).values("dsaname")

    transfer_request = Tbltransferrequest.objects.filter(
                        requestid=requestid
                        ).values("requestid"
                                , "projectnumber"
                                , "requesttype"
                                , "requesttype__requesttypelabel"
                                , "requestedby"
                                , "requesternotes"
                                , "reviewedby"
                                , "reviewdate"
                                , "reviewnotes"
                                , "transfermethod"
                                , "transfermethod__methodlabel"
                                , "transferfrom"
                                , "transferto"
                                , "dsareviewed"
                        ).annotate(requestedby_firstname = Subquery(requestedby_firstname)
                                , requestedby_lastname = Subquery(requestedby_lastname)
                                , reviewedby_firstname = Subquery(reviewedby_firstname)
                                , reviewedby_lastname = Subquery(reviewedby_lastname)
                                , dsa_reviewed = Subquery(dsa_reviewed)
                        ).order_by('-requestid'
                        ).get()
    
    asset_name = Tbltransferfileasset.objects.filter(
        assetid=OuterRef("assetid")
    ).values("assetname")

    transfer_files = Tbltransferfile.objects.filter(
                        validto__isnull=True
                        ,requestid=requestid
                        ).values(
                        ).annotate(asset_name = Subquery(asset_name)
                        ).order_by("asset_name", "filename")

    context = {'transfer_request': transfer_request
                ,'transfer_files': transfer_files
            }

    return render(request, 'Prism/transfer.html', context)

@login_required
@permission_required(["Prism.view_tbluser", "Prism.view_tbldsas", "Prism.view_tblproject"
                      , "Prism.view_tbltransferrequest", "Prism.view_tbltransferfile", "Prism.view_tbltransferfileasset"
                      , "Prism.add_tbltransferrequest", "Prism.add_tbltransferfile", "Prism.add_tbltransferfileasset"], raise_exception=True)
def transfercreate(request, projectnumber):
    project_numbers = Tblproject.objects.filter(
        validto__isnull=True
        , laser = True
    ).values("projectnumber"
    ).order_by("projectnumber")
    
    transfer_form = TransferForm()
    transfer_form.initial['projectnumber'] = projectnumber

    # If projectnumber not yet selected, disable form fields
    if projectnumber == 'new':
        for field in transfer_form.fields:
            transfer_form.fields[field].disabled=True

    # Limit the options in drop downs to just those relevant to the selected project number
    if projectnumber != 'new':
        dsareviewed_choices = Tbldsas.objects.filter(validto__isnull=True, documentid__in=Tbldsasprojects.objects.filter(validto__isnull=True, project__iexact=projectnumber).values("documentid")).order_by("dsaname")
        requestedby_choices =Tbluser.objects.filter(validto__isnull=True, usernumber__in=Tbluserproject.objects.filter(validto__isnull=True, projectnumber__iexact=projectnumber).values("usernumber")).order_by("firstname", "lastname")
        transfer_form.fields['dsareviewed'].queryset = dsareviewed_choices
        transfer_form.fields['requestedby'].queryset = requestedby_choices

    # Initialise with single empty form in formset
    FileFormSet = formset_factory(TransferfileForm, extra=0, can_delete=True)
    formset = FileFormSet()

    context = {'projectnumber': projectnumber
        , 'project_numbers': project_numbers
        , 'transfer_form':transfer_form
        , "formset": formset}

    if request.method == 'POST':
        # Retain inputted transfer details
        transfer_form_new = TransferForm(request.POST)
        transfer_form_new.fields['dsareviewed'].queryset = dsareviewed_choices
        transfer_form_new.fields['requestedby'].queryset = requestedby_choices
        
        if 'files' in request.POST:
            # Expect JSON: {"paths":["sub/a.txt", "b.jpg", ...]}
            try:
                files = json.loads(request.POST.get("files", "[]"))
                assert isinstance(files['paths'], list)
            except Exception:
                return HttpResponseBadRequest("Invalid JSON")

            FileFormSet = formset_factory(TransferfileForm, extra=0, can_delete=True)
            initial = []
            for p in files['paths']:
                initial.append({"filename": p})
            formset = FileFormSet(initial=initial)

            asset_choices = Tbltransferfileasset.objects.filter(assetid__in=Tbltransferfile.objects.filter(validto__isnull=True, requestid__in=Tbltransferrequest.objects.filter(validto__isnull=True, projectnumber__iexact=projectnumber)).values("assetid")).order_by("assetname")
            for form in formset:
                form.fields['assetid'].queryset = asset_choices

            context.update({'transfer_form':transfer_form_new
                ,"formset": formset})

            # Render to a page that shows the formset (no file content uploaded!)
            return render(request, "Prism/transfer_new.html", context)
        
        else:
            FileFormSet = formset_factory(TransferfileForm, extra=0, can_delete=True)
            transfer_files_formset_new = FileFormSet(request.POST)

            if transfer_form_new.is_valid() and transfer_files_formset_new.is_valid():
                with transaction.atomic():
                    parent_transfer = Tbltransferrequest.objects.create(
                        projectnumber = transfer_form_new.cleaned_data['projectnumber']
                        ,requesttype = transfer_form_new.cleaned_data['requesttype']
                        ,requestedby = transfer_form_new.cleaned_data['requestedby'].usernumber
                        ,requesternotes = transfer_form_new.cleaned_data['requesternotes']
                        ,reviewedby = transfer_form_new.cleaned_data['reviewedby'].usernumber
                        ,reviewdate = transfer_form_new.cleaned_data['reviewdate']
                        ,reviewnotes = transfer_form_new.cleaned_data['reviewnotes']
                        ,transfermethod = transfer_form_new.cleaned_data['transfermethod']
                        ,transferfrom = transfer_form_new.cleaned_data['transferfrom']
                        ,transferto = transfer_form_new.cleaned_data['transferto']
                        ,dsareviewed = transfer_form_new.cleaned_data['dsareviewed'].documentid
                        ,validfrom = timezone.now()
                        ,validto = None
                        ,createdby = request.user
                        )

                    for transfer_files_form in transfer_files_formset_new:
                        if transfer_files_form.cleaned_data['DELETE'] == False:
                            Tbltransferfile.objects.create(
                                requestid = parent_transfer
                                ,filename = transfer_files_form.cleaned_data['filename']
                                ,trefilepath = transfer_files_form.cleaned_data['trefilepath']
                                ,datarepofilepath = transfer_files_form.cleaned_data['datarepofilepath']
                                ,transferaccepted = transfer_files_form.cleaned_data['transferaccepted']
                                ,rejectionnotes = transfer_files_form.cleaned_data['rejectionnotes']
                                ,assetid = transfer_files_form.cleaned_data['assetid']
                                ,validfrom = timezone.now()
                                ,validto = None
                                ,createdby = request.user
                            )

                    messages.success(request, 'Transfer added to Prism successfully.')
                    return HttpResponseRedirect(f"/transfer/{parent_transfer.pk}")
            
            else:
                context.update({'projectnumber': projectnumber
                            ,'transfer_form':transfer_form_new
                            ,"formset": transfer_files_formset_new})
                return render(request, "Prism/transfer_new.html", context)

    if request.method == 'GET':
        return render(request, 'Prism/transfer_new.html', context)


def grants_update(request):
    context = {'updated': None
                ,'inserted': None}
    
    if request.method == 'POST':
        context = {'updated': 0
                ,'inserted': 0}

        file = request.FILES['files']
        path = file.file

        pp_df = pd.read_excel(path, skiprows=2)
        pp_df = pp_df.rename(columns=lambda x: x.strip())

        lida_grants = Tblkristal.objects.filter(
            validto__isnull=True
            ).values('kristalref'
            ).order_by('kristalref')
        lida_grants_df = pd.DataFrame(lida_grants)
        
        pp_df = pd.merge(pp_df, lida_grants_df, left_on='Grant', right_on='kristalref', how='inner')

        pp_df_leeds_price = pp_df.groupby(['Grant'], as_index=False
                    ).agg(total_leeds_price=('Leeds Price (£)', 'sum'))

        # Using regex to pattern match 'No ref', replace with None, remove duplicates then prefer External Ref values over None
        pp_df['External Ref.'] = pp_df['External Ref.'].replace(
                                    r'(?i)^(not known|no\b.*\b(ref|reference)\b)',
                                    None,
                                    regex=True
                                    )
        pp_df = pp_df.loc[pp_df["Role"] == "PI", ['Grant Status'
                                ,'Phase Type'
                                ,'Phase Status'
                                ,'Grant'
                                ,'Long Title'
                                ,'External Ref.'
                                ,'Role'
                                ,'Investigator'
                                ,'Location'
                                ,'Faculty'
                                ,'Research Start'
                                ,'Research End'
                                ,'Outline Date'
                                ,'Application Date'
                                ,'Award Date']].drop_duplicates()
        pp_df=pp_df.groupby('Grant').first()

        pp_df_new = pd.merge(pp_df, pp_df_leeds_price, left_on='Grant', right_on='Grant', how='inner')

        pp_existing = tblPortfolioPlus.objects.filter(validto__isnull = True).values()
        pp_df_existing = pd.DataFrame(pp_existing)

        with transaction.atomic():
        # outer join dataframes, left_on = Prism right_on = Portfolio Plus
            df_all = pd.merge(pp_df_existing, pp_df_new, left_on='grant', right_on='Grant', how='outer', indicator=True)
            df_all = df_all.replace({np.nan: None})

            # left_only = present in Prism not in Portfolio Plus = Nothing to do

            # both = present in Prism and in Portfolio Plus  
                # no difference = no action 
                # difference = logically delete in Prism and insert new record 
            df_update = df_all.loc[df_all['_merge'] == 'both']

            if df_update.shape[0] > 0:
                                        # Pandas doesn't always treat None == None, need to explicitly also compare None values (and in our case invert the logic with a tilde)  
                df_update = df_update.loc [(df_update['Grant Status'] != df_update['grantstatus']) & ~(df_update['Grant Status'].isna() & df_update['grantstatus'].isna())
                                            | (df_update['Phase Type'] != df_update['phasetype']) & ~(df_update['Phase Type'].isna() & df_update['phasetype'].isna())
                                            | (df_update['Phase Status'] != df_update['phasestatus']) & ~(df_update['Phase Status'].isna() & df_update['phasestatus'].isna())
                                            | (df_update['Grant'] != df_update['grant']) & ~(df_update['Grant'].isna() & df_update['grant'].isna())
                                            | (df_update['Long Title'] != df_update['longtitle']) & ~(df_update['Long Title'].isna() & df_update['longtitle'].isna())
                                            | (df_update['External Ref.'] != df_update['externalref']) & ~(df_update['External Ref.'].isna() & df_update['externalref'].isna())
                                            | (df_update['Investigator'] != df_update['pi']) & ~(df_update['Investigator'].isna() & df_update['pi'].isna())
                                            | (df_update['Location'] != df_update['location']) & ~(df_update['Location'].isna() & df_update['location'].isna())
                                            | (df_update['Faculty'] != df_update['faculty']) & ~(df_update['Faculty'].isna() & df_update['faculty'].isna())
                                            # Dates are fuckey.  
                                            | (pd.to_datetime(df_update['Research Start']) != pd.to_datetime(df_update['researchstart'])) & ~(df_update['Research Start'].isna() & df_update['researchstart'].isna())
                                            | (pd.to_datetime(df_update['Research End']) != pd.to_datetime(df_update['researchend'])) & ~(df_update['Research End'].isna() & df_update['researchend'].isna())
                                            | (pd.to_datetime(df_update['Outline Date']) != pd.to_datetime(df_update['outlinedate'])) & ~(df_update['Outline Date'].isna() & df_update['outlinedate'].isna())
                                            | (pd.to_datetime(df_update['Application Date']) != pd.to_datetime(df_update['applicationdate'])) & ~(df_update['Application Date'].isna() & df_update['applicationdate'].isna())
                                            | (pd.to_datetime(df_update['Award Date']) != pd.to_datetime(df_update['awarddate'])) & ~(df_update['Award Date'].isna() & df_update['awarddate'].isna())
                                            # Need to convert excel sourced float to decimal for comparison
                                            | (df_update["total_leeds_price"].apply(lambda x: Decimal(str(x)).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP) if x is not None else None) != df_update['leedsprice'])]

                if df_update.shape[0] > 0:
                    for index, row in df_update.iterrows():
                        delete = tblPortfolioPlus.objects.filter(
                            ppid=row['ppid']
                        ).values()
                        delete.update(validto = timezone.now())

                        insert = tblPortfolioPlus(
                            grantstatus = row['Grant Status']
                            ,phasetype = row['Phase Type']
                            ,phasestatus = row['Phase Status']
                            ,grant = row['Grant']
                            ,longtitle = row['Long Title']
                            ,externalref = row['External Ref.']
                            ,pi = row['Investigator']
                            ,location = row['Location']
                            ,faculty = row['Faculty']
                            ,researchstart = row['Research Start']
                            ,researchend = row['Research End']
                            ,outlinedate = row['Outline Date']
                            ,applicationdate = row['Application Date']
                            ,awarddate = row['Award Date']
                            ,leedsprice = row['total_leeds_price']
                            ,validfrom = timezone.now()
                            ,validto = None
                            ,createdby = request.user
                        )
                        insert.save(force_insert=True)
                    # updated_to_display = df_update.to_html()
                    # context['updated'] = updated_to_display
                    context['updated'] = len(df_update.index)
                    
            # right_only = present in Portfolio Plus not in Prism = insert new record    
            df_insert = df_all.loc[df_all['_merge'] == 'right_only']
            if df_insert.shape[0] > 0:
                for index, row in df_insert.iterrows():
                        insert = tblPortfolioPlus(
                            grantstatus = row['Grant Status']
                            ,phasetype = row['Phase Type']
                            ,phasestatus = row['Phase Status']
                            ,grant = row['Grant']
                            ,longtitle = row['Long Title']
                            ,externalref = row['External Ref.']
                            ,pi = row['Investigator']
                            ,location = row['Location']
                            ,faculty = row['Faculty']
                            ,researchstart = row['Research Start']
                            ,researchend = row['Research End']
                            ,outlinedate = row['Outline Date']
                            ,applicationdate = row['Application Date']
                            ,awarddate = row['Award Date']
                            ,leedsprice = row['total_leeds_price']
                            ,validfrom = timezone.now()
                            ,validto = None
                            ,createdby = request.user
                        )
                        insert.save(force_insert=True)

                # inserted_to_display = df_insert.to_html()
                # context['inserted'] = inserted_to_display
                context['inserted'] = len(df_insert.index)

    return render(request, 'Prism/grants_update.html', context)