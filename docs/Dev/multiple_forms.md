---
layout: default
title: Multiple Forms
nav_order: 5
parent: Development
has_children: false
---

# Multiple forms in single template
- TOC
{:toc}

## Prefixes
We've had to establish multiple forms in a single view so that we can display and update project details and project notes independantly from the same page.  

To maintain independance we're instantiating forms `ProjectForm` and `ProjectNotesForm` with prefixes (`'project'` and `'p_note'` respectively). this prefixes all field names in the form with those values, so `ProjectForm.projectnumber` becomes `ProjectForm.project-projectnumber` for example. We can then use `if` statements on prefixed field names to conditionally split the workflow depending on which form is being submitted, eg:

```python
if request.method == "POST":
        if 'project-pid' in request.POST:
            # 
            # do project details stuff here
            # 
        elif 'p_note-pnote' in request.POST:
            # 
            # do project note stuff here
            # 
```

Make sure each form gets it's own <!-- {% raw %} --> `{% csrf_token %}`<!-- {% endraw %} --> to avoid Cross Site Request Forgery.  

The Notes form only has a single input control with a submit button all to itself. The notes themselves are displayed using an html table, iterating over an instance of the `Tblprojectnotes` model to populate.  

Pagination is a handy way to keep things readable and not clutter the screen; it is handled in the view.  

## Formsets  
When logging transfers we need to be able to submit multiple records with a single request. One Transfer Request for _**many Transfer Files**_, possibly grouped into assets. To do this we can use formsets, constructed by `formset_factory`.  

Each Transfer File gets a form (`TransferfileForm`) for each file name in `{'files'}` of the POST request. The Transfer File forms are grouped into formsets and handled iteratively within the view and template.  

If `can_delete=True` on `formset_factory` instantiation, each form in a formset has a `DELETE` field that if True skips validation. Removing a file from the New Transfer Files Table actually just sets this `DELETE` field to True and hides the row from the table. Logic in the View skips these forms from being inserted to the database.  

## Submitting multiple forms
In most pages we wish to submit just a single form on a page at a time; for example project notes form wants to be handled seperately from the project membership form. In these cases it makes sense for each form to have it's own `csrf_token` and Submit button. For transfers though we want to populate up to three tables in the database at once; Request, Files & Assets.  

This is acheived simply by wrapping all forms and formsets rendered in the template within a single `<form>` tag with a single `csrf_token` and Submit button. All forms and formsets will be in the POST request to be handled by the view.  

Enclosing the creation of Request and File records within a `with transaction.atomic():` block means that if _any_ insert fails then all inserts are rolled back; no changes to database.  