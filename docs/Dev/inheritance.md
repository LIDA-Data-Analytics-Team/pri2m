---
layout: default
title: Template Inheritance
nav_order: 3
parent: Development
has_children: false
---

- TOC
{:toc}

# Template inheritance  
Django lets us adhere to DRY principles in html templating through inheritance.  

By creating a top level html template that sets out styling and navigation, that all other templates inherit, consistency can be maintained. In this project the top level template is called `layout.html` and is saved with all the other html templates in `templates/Prism`.  

The `layout.html` template defines blocks that can be referenced in other html templates that inherit from it. In this way item positions and styles can be maintained across the site through the use of <!-- {% raw %} --> `{% block name %}{% endblock %}`<!-- {% endraw %} --> tags. All templates know to insert the content of these blocks into the corresponding block of the inherited template, as long as <!-- {% raw %} --> `{% extends "Prism/layout.html" %}`<!-- {% endraw %} --> is included at the top of the template.  

`layout.html` has been used to define the navigation bar at the top of the page. Because every page of the site inherits this template, every page of the site has the same nav bar and any changes to it need only be made once.  
