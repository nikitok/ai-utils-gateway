# Directual UI Helm Chart

This Helm chart deploys Directual UI to Kubernetes using ArgoCD with base + overlays pattern.

## Structure

```
.helm/
├── base/                       # Base Helm chart
│   ├── Chart.yaml             # Base chart metadata
│   ├── values.yaml            # Base default values
│   └── templates/             # Kubernetes resource templates
│       ├── deployment.yml
│       ├── service.yaml
│       ├── ingress-base.yaml
│       ├── hpa.yaml
│       └── ...
└── overlays/                   # Environment-specific overlays
    ├── alfa/                   # Alfa (staging) overlay
    │   ├── Chart.yaml         # References base chart as dependency
    │   └── values.yaml        # Alfa-specific values
    └── prod/                   # Production overlay
        ├── Chart.yaml         # References base chart as dependency
        └── values.yaml        # Production-specific values
```

## Architecture

### Base Chart
The base chart (`.helm/base/`) contains:
- All Kubernetes templates
- Default configuration values
- Common settings shared across environments

### Overlays
Each overlay (`.helm/overlays/{env}/`) contains:
- `Chart.yaml` that declares the base chart as a dependency
- `values.yaml` that overrides base values for that environment

## Deployment Process

1. **Build Stage**: When a tag is pushed, GitLab CI builds and pushes Docker image
2. **Update Alfa**: Automatically updates `.helm/overlays/alfa/values.yaml` with new image tag
3. **Promote to Prod**: Manual step to update `.helm/overlays/prod/values.yaml` with the same tag

## Environment Configuration

### Alfa Environment
- Path: `.helm/overlays/alfa/`
- 2 replicas
- Lower resource limits (256Mi-512Mi memory)
- Domain: my.alfa.directual.com
- Auto-sync enabled in ArgoCD

### Production Environment
- Path: `.helm/overlays/prod/`
- 3-10 replicas with HPA
- Higher resource limits (512Mi-1Gi memory)
- Domain: app.directual.com
- Manual sync in ArgoCD
- Pod anti-affinity for high availability

## ArgoCD Integration

ArgoCD applications point directly to overlay directories:
- Alfa: `.helm/overlays/alfa/`
- Prod: `.helm/overlays/prod/`

ArgoCD automatically handles the dependency resolution and applies both base and overlay values.

## Manual Deployment (without ArgoCD)

```bash
# First, update dependencies for the overlay
cd .helm/overlays/staging


# Deploy to alfa
helm dependency update && helm  -n alfa upgrade --install directual-ui-utils .

# For production
cd .helm/overlays/prod
helm dependency update

# Deploy to production
helm upgrade --install directual-ui-utils . \
  -n directual-prod --create-namespace
```

## Updating Image Tags

The CI/CD pipeline automatically updates image tags in overlay values files:
- Alfa: `.helm/overlays/alfa/values.yaml`
- Prod: `.helm/overlays/prod/values.yaml`

Manual update example:
```bash
# Update alfa
sed -i 's|tag: .*|tag: "v1.2.3"|g' .helm/overlays/alfa/values.yaml

# Update prod
sed -i 's|tag: .*|tag: "v1.2.3"|g' .helm/overlays/prod/values.yaml
```

## Required Secrets

Before deploying, ensure these secrets exist:

```bash
# Create image pull secret
kubectl create secret docker-registry gitlab-registry \
  --docker-server=gitlab.directual.com:5005 \
  --docker-username=<username> \
  --docker-password=<password> \
  -n <namespace>
```

## CI/CD Variables

Required GitLab CI/CD variables:
- `DEPLOY_SSH_KEY` - SSH key for pushing to repository
- `SSH_KNOWN_HOSTS` - SSH known hosts for GitLab