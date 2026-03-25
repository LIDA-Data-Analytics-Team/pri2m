---
layout: default
title: Validation
nav_order: 6
parent: Development
has_children: false
---

- TOC
{:toc}

# Validation  

## Context setting  
Frequently we will want multiple forms to be displayed and submitted from a single page. For example, on a project page we will want to display project details from a `ProjectForm` instance with initial values populated and have it submit new values when changed. On the same page we would want those project details displayed alongside, for example, the project notes form (`ProjectNotesForm`) and have that populated with initial values and separately submittable.  

Multiple forms can be handles in the view for the page through the use of prefixes as described above. It does present a challenge when trying to redirect back to the page in the event of failed validation. The issue is that when redirecting from a failed form validation the context for the page is missing. This results in the submitted form being returned with the original data displayed, no validation errors displayed, no submitted data and no feedback as to why.  

The solution is to not redirect on validation failure, but render using the same instance of the form that failed the validation so the errors can be displayed.  

To this end I have moved all `context` setting to the top of the View before making any POST/GET pathing checks. In the event of a POST request the prefixes route the request to the correct Form handling in the View and form validation occurs (with the `.is_valid()` function). On failure the page is rendered again, but with the failed form replacing the initial form in the `context`.  

We now create every form on every request, then override only the one that was submitted.  


## Custom validation in the Form  
We can override the `clean()` method on a Form. If we ensure to include `cleaned_data = super().clean()` at the start then what follows will simply add to the existing validation rather than replace it. Example `forms.py`:  

```python
class MyForm(forms.Form):
    id = forms.IntegerField()
    field= forms.CharField(label="Field", max_length=5)
    
    def clean(self):
        cleaned_data = super().clean()
        # 
        # do custom validation stuff on cleaned_data here
        # 
        return self.cleaned_data
```

It's possible to add `non_field_errors` that exist at the Form scope by including `None` in the field parameter of `.add_error()` like so:
```python
self.add_error(None, "Custom error message.")
```

These `non_field_errors` can be accessed from the template like so:
<!-- {% raw %} -->
```html
{% if form.non_field_errors %}
    {% for error in form.non_field_errors %}
        {{error}}
    {% endfor %}
{% endif %}
```
<!-- {% endraw %} -->

If the form has been created in the template via Django's built in methods (e.g. `{{ form.as_p}}`) then any `non_field_errors` will be displayed at the top of the form automatically.  

Failure of these validation checks _will_ cause the submission to fail; _no_ changes to the database will be made. Any item added to `_errors` (as we have here) will cause `is_valid==False`.  


## Custom validation in the View  
Sometimes we may want to feedback on data issues without preventing submission of the data. For example, if there is a missing time period where contiguous time periods are expected it would be importnant to highlight that without preventing data being submitted that might partially resolve it as a step to completely resolving it!  

In these cases we can put validation checks in the GET request path of the View and pass them in to the context of the rendered page. This is acheived by adding an empty list in the context setting of the View and adding items to it in the custom validation of the View. I put them in the GET route because there's no benefit running them multiple times on a POST request. Example `views.py`:

```python
def MyView(request):
    custom_errors = []

    context = {'custom_errors': custom_errors}

    if request.method == 'GET':
        if validation_check_fails:
            custom_errors.append("Custom error message")

    return render(request, 'url.html', context)
```

As above, these `custom_errors` can be accessed from the template like so:
<!-- {% raw %} -->
```html
{% if custom_errors %}
    {% for error in custom_errors %}
        {{error}}
    {% endfor %}
{% endif %}
```
<!-- {% endraw %} -->

Failure of these validation checks will _not_ cause the submission to fail; changes to the database _will_ be made. We're just passing through our own list of strings.    


## Validate initial data  
When creating the form with initial data, we may still want to validate the form.  

This `__init__` override will populate a temporary form (`temp`) with `data=initial` (as if it were a POST request) to trigger validation.  

Any errors are copied back in to the original form and displayed with the data from the database.  

```python
def __init__(self, *args, **kwargs): 
    super().__init__(*args, **kwargs)
    if self.initial: 
        temp = type(self)(data=self.initial) 
        if not temp.is_valid(): 
            self._errors = temp.errors
```
