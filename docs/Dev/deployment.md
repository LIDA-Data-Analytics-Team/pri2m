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

## Key dependencies  

To authenticate the app against the Azure SQL Database:
- `DefaultAzureCredential()` (from `azure.identity`) to generate an  
- `AccessToken` (from `azure.core.credentials`)  

To authenticate the user via Entra:  
- `DefaultAzureCredential()` (from `azure.identity`)
- `SecretClient` (from `azure.keyvault.secrets`)

To connect to Azure SQL Database:
- `ODBC Driver 18 for SQL Server`


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


