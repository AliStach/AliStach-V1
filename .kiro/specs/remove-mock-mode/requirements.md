# Requirements Document

## Introduction

This specification defines the complete removal of all mock-mode functionality from the AliExpress API Proxy project. The system currently includes fallback mechanisms that return simulated data when real API calls fail or when mock mode is explicitly enabled. This creates confusion, reduces reliability, and masks real API issues. The goal is to eliminate all mock data generation, preset responses, and automatic fallbacks, ensuring the system exclusively returns real AliExpress API data or authentic error responses.

## Glossary

- **System**: The AliExpress API Proxy application
- **Mock Mode**: A feature that returns simulated/fake AliExpress data instead of real API responses
- **MockDataService**: A service module that generates preset fake product and category data
- **AliExpressService**: The primary service class that interfaces with the real AliExpress API
- **AliExpressServiceWithMock**: An extended service class that adds mock mode capabilities
- **FORCE_MOCK_MODE**: An environment variable that enables mock mode when set to "true"
- **Fallback Logic**: Code that automatically switches to mock data when real API calls fail
- **Real API Response**: Data returned directly from AliExpress API endpoints
- **Authentic Error**: A genuine error response from the AliExpress API or network layer

## Requirements

### Requirement 1

**User Story:** As a developer integrating with the proxy, I want all responses to come from the real AliExpress API, so that I can trust the data accuracy and identify real API issues.

#### Acceptance Criteria

1. WHEN the System receives any API request, THE System SHALL call only the real AliExpress API endpoints
2. THE System SHALL NOT generate simulated product data under any circumstance
3. THE System SHALL NOT generate simulated category data under any circumstance
4. IF the real AliExpress API call fails, THEN THE System SHALL return an authentic error response with the actual failure reason
5. THE System SHALL NOT contain any code paths that automatically switch to mock data when API calls fail

### Requirement 2

**User Story:** As a system administrator, I want all mock-related configuration options removed, so that there is no possibility of accidentally enabling mock mode in production.

#### Acceptance Criteria

1. THE System SHALL NOT recognize the FORCE_MOCK_MODE environment variable
2. THE System SHALL NOT accept any force_mock parameter in service initialization
3. THE System SHALL NOT contain any mock_mode property or attribute in service classes
4. THE System SHALL NOT include any configuration options related to mock data generation
5. WHEN the System starts, THE System SHALL NOT log any messages about mock mode status

### Requirement 3

**User Story:** As a maintainer, I want all mock-related files and modules deleted, so that the codebase is cleaner and there is no dead code.

#### Acceptance Criteria

1. THE System SHALL NOT contain the MockDataService module file
2. THE System SHALL NOT contain the AliExpressServiceWithMock module file
3. THE System SHALL NOT import MockDataService in any module
4. THE System SHALL NOT import AliExpressServiceWithMock in any module
5. THE System SHALL NOT contain any test files specifically for testing mock mode functionality

### Requirement 4

**User Story:** As a developer, I want the AliExpressService to be simplified without mock logic, so that the code is easier to understand and maintain.

#### Acceptance Criteria

1. THE AliExpressService class SHALL NOT contain any mock_mode instance variable
2. THE AliExpressService constructor SHALL NOT accept a force_mock parameter
3. THE AliExpressService constructor SHALL NOT check the FORCE_MOCK_MODE environment variable
4. WHEN any AliExpressService method executes, THE method SHALL NOT check whether mock mode is enabled
5. THE AliExpressService methods SHALL NOT contain conditional branches that return mock data

### Requirement 5

**User Story:** As a quality assurance engineer, I want all test files updated to remove mock mode dependencies, so that tests validate only real API behavior.

#### Acceptance Criteria

1. THE System SHALL NOT contain test files that set FORCE_MOCK_MODE environment variable
2. THE System SHALL NOT contain test files that import AliExpressServiceWithMock
3. THE System SHALL NOT contain test files that verify mock data responses
4. WHERE test files reference mock mode in comments or documentation, THE System SHALL remove those references
5. THE System SHALL NOT contain any test utilities for generating mock data

### Requirement 6

**User Story:** As an operations engineer, I want clear error messages when API calls fail, so that I can diagnose and fix real integration issues.

#### Acceptance Criteria

1. WHEN the AliExpress API returns an error, THE System SHALL propagate the actual error message to the client
2. WHEN the AliExpress API is unreachable, THE System SHALL return a network error with connection details
3. WHEN API credentials are invalid, THE System SHALL return an authentication error with credential validation guidance
4. THE System SHALL NOT mask API failures by returning simulated data
5. THE System SHALL log all API failures with complete error details for debugging

### Requirement 7

**User Story:** As a developer, I want the service initialization to fail fast with clear errors when credentials are missing, so that I know immediately if configuration is incorrect.

#### Acceptance Criteria

1. WHEN the System initializes without valid ALIEXPRESS_APP_KEY, THE System SHALL raise a ConfigurationError
2. WHEN the System initializes without valid ALIEXPRESS_APP_SECRET, THE System SHALL raise a ConfigurationError
3. THE System SHALL NOT fall back to mock mode when credentials are missing
4. THE System SHALL NOT allow the service to start in a degraded mode with mock data
5. WHEN credential validation fails, THE System SHALL provide clear guidance on how to obtain valid credentials

### Requirement 8

**User Story:** As a code reviewer, I want all documentation and comments updated to remove mock mode references, so that documentation accurately reflects the system behavior.

#### Acceptance Criteria

1. THE System SHALL NOT contain README sections describing mock mode functionality
2. THE System SHALL NOT contain code comments explaining how to enable mock mode
3. THE System SHALL NOT contain API documentation mentioning mock data responses
4. WHERE documentation files contain mock mode instructions, THE System SHALL remove those sections
5. THE System SHALL update all relevant documentation to clarify that only real API data is returned

### Requirement 9

**User Story:** As a deployment engineer, I want example environment files cleaned of mock mode variables, so that new deployments are configured correctly from the start.

#### Acceptance Criteria

1. THE System SHALL NOT include FORCE_MOCK_MODE in .env.example files
2. THE System SHALL NOT include FORCE_MOCK_MODE in .env.secure.example files
3. THE System SHALL NOT include mock mode configuration in deployment documentation
4. THE System SHALL NOT reference mock mode in deployment scripts
5. WHERE environment templates mention mock mode, THE System SHALL remove those references
