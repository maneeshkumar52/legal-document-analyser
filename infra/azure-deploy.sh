#!/bin/bash
set -e
echo "Deploying Legal Document Analyser..."
az group create --name rg-legal-analyser --location uksouth
az containerapp create --name legal-document-analyser --resource-group rg-legal-analyser --image python:3.11-slim --target-port 8000 --ingress external
echo "Done!"
