#!/bin/bash

# Build and deploy script for Kubernetes scraper

set -e

eval $(minikube docker-env)

echo "🚀 Building Docker image..."
docker build -t adresowo-scraper:latest .

echo "📦 Deploying to Kubernetes..."

# Apply all manifests
kubectl apply -k k8s/

echo "✅ Deployment completed!"
echo ""
echo "📋 Useful commands:"
echo "  kubectl get jobs -n scraper                    # Check job status"
echo "  kubectl get pods -n scraper                    # Check pod status"
echo "  kubectl logs -n scraper -l city=warszawa       # View Warsaw scraper logs"
echo "  kubectl logs -n scraper -l city=wroclaw        # View Wrocław scraper logs"
echo "  kubectl describe job scraper-warszawa -n scraper  # Describe Warsaw job"
echo "  kubectl describe job scraper-wroclaw -n scraper   # Describe Wrocław job"
echo ""
echo "🔄 To run jobs manually:"
echo "  kubectl create job --from=job/scraper-warszawa scraper-warszawa-manual -n scraper"
echo "  kubectl create job --from=job/scraper-wroclaw scraper-wroclaw-manual -n scraper"
echo ""
echo "📁 To access data:"
echo "  kubectl cp scraper/<pod-name>:/data ./data -n scraper"