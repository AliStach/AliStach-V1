# Design Document

## Overview

The current Vercel deployment generates unique URLs for each deployment (e.g., `aliexpress-api-proxy-g7uc3ixok-chana-jacobs-projects.vercel.app`) because no permanent alias is configured. This design establishes a stable production URL through Vercel's alias system, ensuring external integrations remain functional across deployments.

## Root Cause Analysis

**Primary Issue**: Vercel generates unique deployment URLs by default, combining:
- Project name: `aliexpress-api-proxy`
- Random deployment hash: `g7uc3ixok` (changes per deployment)
- Team/user namespace: `chana-jacobs-projects`
- Vercel domain: `vercel.app`

**Why URLs Change**: Each deployment receives a new unique hash to enable:
- Deployment rollbacks
- A/B testing capabilities
- Immutable deployment references
- Parallel deployment testing

**Missing Configuration**: No alias configuration exists to create a permanent URL that automatically points to the latest deployment.

## Architecture

### Current State
```
Deployment 1: aliexpress-api-proxy-abc123-chana-jacobs-projects.vercel.app
Deployment 2: aliexpress-api-proxy-def456-chana-jacobs-projects.vercel.app
Deployment 3: aliexpress-api-proxy-g7uc3ixok-chana-jacobs-projects.vercel.app
```

### Target State
```
Permanent URL: aliexpress-api-proxy.vercel.app (or custom domain)
                     ↓ (automatically redirects to latest)
Latest Deployment: aliexpress-api-proxy-xyz789-chana-jacobs-projects.vercel.app
```

## Components and Interfaces

### 1. Vercel Configuration Enhancement

**File**: `vercel.json`
- Add alias configuration for production deployments
- Configure automatic alias assignment for main branch deployments
- Maintain existing build and routing configuration

### 2. Domain Alias Options

**Option A: Vercel Subdomain Alias**
- Format: `aliexpress-api-proxy.vercel.app`
- Automatic assignment to production deployments
- No additional domain costs
- Professional appearance

**Option B: Custom Domain (Future Enhancement)**
- Format: `api.alistach.com` or similar
- Requires domain ownership
- Enhanced branding
- Additional DNS configuration

### 3. Deployment Pipeline Integration

**Production Branch**: `main` or `master`
- Automatic alias assignment on successful deployment
- Immediate URL availability
- Zero-downtime updates

**Development Branches**: Feature branches
- Retain unique URLs for testing
- No alias assignment
- Isolated testing environments

## Data Models

### Vercel Configuration Schema
```json
{
  "version": 2,
  "alias": ["aliexpress-api-proxy.vercel.app"],
  "builds": [...],
  "routes": [...],
  "env": {...}
}
```

### Domain Configuration
```json
{
  "domains": [
    {
      "name": "aliexpress-api-proxy.vercel.app",
      "redirect": "latest-deployment-url",
      "type": "alias"
    }
  ]
}
```

## Error Handling

### Alias Assignment Failures
- **Scenario**: Alias already in use or configuration error
- **Response**: Deployment succeeds but alias assignment fails
- **Resolution**: Manual alias assignment through Vercel dashboard
- **Prevention**: Validate alias availability during configuration

### DNS Propagation Delays
- **Scenario**: New alias takes time to propagate globally
- **Response**: Temporary unavailability (typically < 5 minutes)
- **Resolution**: Automatic resolution as DNS propagates
- **Mitigation**: Use Vercel's global CDN for faster propagation

### Rollback Scenarios
- **Scenario**: Need to rollback to previous deployment
- **Response**: Alias automatically points to rolled-back deployment
- **Resolution**: Immediate URL availability for rollback
- **Process**: Use Vercel dashboard or CLI for rollback operations

## Testing Strategy

### 1. Configuration Validation
- Verify `vercel.json` syntax and alias configuration
- Test deployment with alias assignment
- Validate URL accessibility immediately after deployment

### 2. Integration Testing
- Test GPT Actions integration with permanent URL
- Verify OpenAPI specification accessibility
- Confirm all documented endpoints work with new URL

### 3. Deployment Testing
- Deploy multiple times to confirm alias persistence
- Test rollback scenarios with alias reassignment
- Verify zero-downtime during deployment updates

### 4. Documentation Updates
- Update README.md with permanent URL
- Modify all endpoint documentation
- Update GPT Actions configuration examples

## Implementation Approach

### Phase 1: Alias Configuration
1. Update `vercel.json` with alias configuration
2. Deploy and verify alias assignment
3. Test permanent URL functionality

### Phase 2: Documentation Updates
1. Update all URL references in documentation
2. Modify README.md production URLs
3. Update GPT Actions integration examples

### Phase 3: Validation and Testing
1. Comprehensive endpoint testing with new URL
2. GPT Actions integration verification
3. Performance and availability monitoring

## Expected Outcome

**Final Permanent URL**: `aliexpress-api-proxy.vercel.app`

**Benefits**:
- Stable URL across all deployments
- Automatic updates to latest deployment
- Zero configuration required for external integrations
- Professional, predictable URL structure
- Maintained deployment history and rollback capabilities

**URL Structure**:
- **Production**: `https://aliexpress-api-proxy.vercel.app`
- **Health Check**: `https://aliexpress-api-proxy.vercel.app/health`
- **API Docs**: `https://aliexpress-api-proxy.vercel.app/docs`
- **OpenAPI Spec**: `https://aliexpress-api-proxy.vercel.app/openapi-gpt.json`