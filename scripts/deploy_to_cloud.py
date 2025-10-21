#!/usr/bin/env python3
"""
Cloud deployment script for COVID-19 ABM.
"""

import argparse
import subprocess
import sys
import os
import json
from typing import Dict, List

def run_command(command: List[str], cwd: str = None) -> bool:
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {' '.join(command)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return False

def deploy_to_aws(region: str = "us-west-2", environment: str = "dev"):
    """Deploy to AWS using CloudFormation and ECS"""
    print("🚀 Deploying to AWS...")
    
    # Build and push Docker image to ECR
    print("📦 Building and pushing Docker image to ECR...")
    
    # Get AWS account ID
    account_id_cmd = ["aws", "sts", "get-caller-identity", "--query", "Account", "--output", "text"]
    result = subprocess.run(account_id_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Failed to get AWS account ID. Make sure AWS CLI is configured.")
        return False
    
    account_id = result.stdout.strip()
    ecr_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/covid-abm"
    
    # Create ECR repository if it doesn't exist
    run_command(["aws", "ecr", "create-repository", "--repository-name", "covid-abm", "--region", region])
    
    # Login to ECR
    run_command(["aws", "ecr", "get-login-password", "--region", region, "|", "docker", "login", "--username", "AWS", "--password-stdin", ecr_uri])
    
    # Build and push image
    run_command(["docker", "build", "-t", "covid-abm", "-f", "docker/Dockerfile", "."])
    run_command(["docker", "tag", "covid-abm:latest", f"{ecr_uri}:latest"])
    run_command(["docker", "push", f"{ecr_uri}:latest"])
    
    # Deploy CloudFormation stack
    print("☁️  Deploying CloudFormation stack...")
    stack_name = f"covid-abm-{environment}"
    
    run_command([
        "aws", "cloudformation", "deploy",
        "--template-file", "cloud/aws/cloudformation.yaml",
        "--stack-name", stack_name,
        "--parameter-overrides", f"Environment={environment}",
        "--capabilities", "CAPABILITY_IAM",
        "--region", region
    ])
    
    print("✅ AWS deployment completed!")

def deploy_to_gcp(project_id: str, region: str = "us-central1"):
    """Deploy to Google Cloud Platform"""
    print("🚀 Deploying to GCP...")
    
    # Set project
    run_command(["gcloud", "config", "set", "project", project_id])
    
    # Enable required APIs
    print("🔧 Enabling required APIs...")
    apis = [
        "cloudbuild.googleapis.com",
        "run.googleapis.com",
        "container.googleapis.com",
        "storage.googleapis.com"
    ]
    
    for api in apis:
        run_command(["gcloud", "services", "enable", api])
    
    # Build and push to Container Registry
    print("📦 Building and pushing to Container Registry...")
    run_command([
        "gcloud", "builds", "submit",
        "--tag", f"gcr.io/{project_id}/covid-abm",
        "--file", "cloud/gcp/cloudbuild.yaml"
    ])
    
    # Deploy to Cloud Run
    print("☁️  Deploying to Cloud Run...")
    run_command([
        "gcloud", "run", "deploy", "covid-abm",
        "--image", f"gcr.io/{project_id}/covid-abm",
        "--region", region,
        "--platform", "managed",
        "--allow-unauthenticated",
        "--memory", "8Gi",
        "--cpu", "4",
        "--timeout", "3600"
    ])
    
    print("✅ GCP deployment completed!")

def deploy_to_azure(resource_group: str, location: str = "eastus"):
    """Deploy to Microsoft Azure"""
    print("🚀 Deploying to Azure...")
    
    # Create resource group
    run_command(["az", "group", "create", "--name", resource_group, "--location", location])
    
    # Build and push to Azure Container Registry
    print("📦 Building and pushing to Azure Container Registry...")
    acr_name = f"covidabm{resource_group.replace('-', '')}"
    
    # Create ACR
    run_command(["az", "acr", "create", "--resource-group", resource_group, "--name", acr_name, "--sku", "Basic"])
    
    # Login to ACR
    run_command(["az", "acr", "login", "--name", acr_name])
    
    # Build and push image
    run_command(["docker", "build", "-t", "covid-abm", "-f", "docker/Dockerfile", "."])
    run_command(["docker", "tag", "covid-abm", f"{acr_name}.azurecr.io/covid-abm:latest"])
    run_command(["docker", "push", f"{acr_name}.azurecr.io/covid-abm:latest"])
    
    # Deploy to Container Instances
    print("☁️  Deploying to Azure Container Instances...")
    run_command([
        "az", "container", "create",
        "--resource-group", resource_group,
        "--name", "covid-abm-simulation",
        "--image", f"{acr_name}.azurecr.io/covid-abm:latest",
        "--cpu", "4",
        "--memory", "8",
        "--restart-policy", "Never",
        "--environment-variables",
        "POPULATION_SIZE=100000",
        "SIMULATION_DAYS=365",
        "N_SEEDS=10"
    ])
    
    print("✅ Azure deployment completed!")

def main():
    parser = argparse.ArgumentParser(description="Deploy COVID-19 ABM to cloud platforms")
    parser.add_argument("--aws", action="store_true", help="Deploy to AWS")
    parser.add_argument("--gcp", action="store_true", help="Deploy to Google Cloud Platform")
    parser.add_argument("--azure", action="store_true", help="Deploy to Microsoft Azure")
    parser.add_argument("--region", default="us-west-2", help="Cloud region (default: us-west-2)")
    parser.add_argument("--environment", default="dev", help="Environment name (default: dev)")
    parser.add_argument("--project-id", help="GCP project ID (required for GCP deployment)")
    parser.add_argument("--resource-group", help="Azure resource group (required for Azure deployment)")
    
    args = parser.parse_args()
    
    if not any([args.aws, args.gcp, args.azure]):
        print("❌ Please specify a cloud platform: --aws, --gcp, or --azure")
        sys.exit(1)
    
    if args.gcp and not args.project_id:
        print("❌ GCP project ID is required for GCP deployment. Use --project-id")
        sys.exit(1)
    
    if args.azure and not args.resource_group:
        print("❌ Azure resource group is required for Azure deployment. Use --resource-group")
        sys.exit(1)
    
    print("☁️  COVID-19 ABM Cloud Deployment")
    print("=" * 50)
    
    if args.aws:
        deploy_to_aws(args.region, args.environment)
    
    if args.gcp:
        deploy_to_gcp(args.project_id, args.region)
    
    if args.azure:
        deploy_to_azure(args.resource_group, args.region)
    
    print("\n🎉 Deployment completed successfully!")

if __name__ == "__main__":
    main()
