---
layout: default
title: Styling
nav_order: 4
parent: Development
has_children: false
---

- TOC
{:toc}

# Static files  
A css style sheet has been created and is referenced in the parent template `layout.html` so all pages that inherit will be subject to the same styling choices. `style.css` has been saved to `static/Prism` along with a `prism.ico` favicon.  

Static files need to be loaded explicitly with <!-- {% raw %} --> `{% load static %}`<!-- {% endraw %} -->, but as this is done in the parent template it need only be done once here. When out of dev (ie when `DEBUG=False` in `settings.py`) there will be a need to load a third party library such as **WhiteNoise** to load static files.  


# Bootstrap 5
By installing `django-bootstrap-v5` to the python env we have access to bootstrap 5 styling.  

I've found this especially useful for laying out the controls using a grid (`col-md-auto` FTW), but I'm hoping it will come into it's own with comboboxes for named individuals on a project. The drop down boxes are kinda hard to use when dealing with so many options; we really need some form of autocomplete drop down.  
