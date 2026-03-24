---
layout: default
title: Deployment
nav_order: 8
parent: Django initiation
has_children: false
---

- TOC
{:toc}

# Deployment  
Currently just testing and playing with the clay, so all resources are created and configured via Azure Portal. Will need to script for IaC before going live with anything.  

## Key dependencies  
As described in Authentication the Pri2m app connects to Azure SQL Database using tokens. These tokens are generated from credentials that are authenticated using `DefaultAzureCredential()`. When deployed, the Managed Identity of the Web Service is used but the connection is made using `ODBC Driver 18 for SQL Server`.  

Azure Web Service doesn't come equipped with ODBC drivers (!) so we have had to use Docker to containerise the app and install `msodbcsql18` and `unixodbc-dev`.  


## Azure Resources  
The following resources are needed (minimum):
- App Service
- App Service Plan
- Container Registry
- Key Vault
- App Registration

All configurations subject to change obvs, but this is what I chose for testing purposes. All else was accepted default values.  

### Key Vault  
- Basics  
    - Region: UK South
    - Pricing tier: Standard
- Access configuration
    - Permission model: Azure role-based access control

### Container Registry  
- Basics  
    - Location: UK South
    - Pricing plan: Basic
    - Role assignment permissions mode: RBAC Registry Permissions

### App Service & Plan
Create just the Web App, no need for a database as we're using an existing one.  

- Basics  
    - Publish: Container
    - Operating System: Linux
    - Region: UK South
    - Linux plan: Create new
    - Pricing plan: Basic B1
    - Zone redundancy: Disabled
- Container
    - Image Source: Azure Container Registry
    - Name: main
    - Registry: Same as created above
    - Authentication: Managed identity
    - Identity: New (we'll add a System Managed Identity later and delete this one)
    - Image: image name in CR
    - Tag: latest
    - Port: 8000 (CRITICAL!) 

Once created, make sure to go into resource and check `Continuous deployment for the main container` under `Deployment Centre`.  

## Permissions  

|Resource|Permission Type|Permission|Granted to|
|---|---|---|---|
|App Service|System Managed Identity|db_datareader <br>db_datawriter|Azure SQL Database|
|App Service|System Managed Identity|Key Vault Secrets User|Key Vault|
|App Service|System Managed Identity|AcrPull|Container Registry|
|App Registration|Client Secret|read.user|MS Graph|

## Docker deployment
Build image from dockerfile  
`docker build -t pri2m-docker .`  

Sign in to Container Registry  
`docker login pri2m.azurecr.io --username pri2m`  
(password found in Portal --> Access Tokens)

Tag image to Container Registry  
`docker tag pri2m-docker pri2m.azurecr.io/pri2m-docker:latest`  

Push the image to the Container Registry  
`docker push pri2m.azurecr.io/pri2m-docker:latest`  

Because the `Continuous deployment for the main container` has been checked in the App Service --> Deployment Centre, all pushes to the Container Registry (that match name & tag) will automagically roll out.  
