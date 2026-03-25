---
layout: default
title: Multiple Forms
nav_order: 5
parent: Development
has_children: false
---

- TOC
{:toc}

# Prefixes
We've had to establish multiple forms in a single view so that we can display and update project details and project notes on the same page.  

To do this we're instantiating forms `ProjectForm` and `ProjectNotesForm` with prefixes (`'project'` and `'p_note'` respectively). this prefixes all field names in the form with those values, so `ProjectForm.projectnumber` becomes `ProjectForm.project-projectnumber` for example. We can then use `if` statements on prefixed field names to conditionally split the workflow depending on which form is being submitted, eg:

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
