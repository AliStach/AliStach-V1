# Implementation Plan: Remove Mock Mode

## Task List

- [x] 1. Refactor AliExpressService to remove mock mode logic


  - Remove all mock mode conditional branches and properties from the core service class
  - Simplify service initialization to require valid credentials
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4, 4.5_



- [ ] 1.1 Remove mock mode imports and initialization from AliExpressService
  - Delete `from .mock_data_service import MockDataService` import statement
  - Remove `force_mock` parameter from `__init__` method signature
  - Remove `self.mock_mode` instance variable initialization
  - Remove `FORCE_MOCK_MODE` environment variable check
  - Remove fallback logic that sets `self.mock_mode = True` on API initialization failure
  - Remove mock mode logging statements

  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 1.2 Remove mock data branches from get_parent_categories method
  - Delete the entire `if self.mock_mode:` block that calls `MockDataService.get_parent_categories()`
  - Keep only the real API implementation path

  - Ensure error handling propagates authentic errors without fallback
  - _Requirements: 1.1, 1.2, 1.3, 4.4, 4.5_

- [ ] 1.3 Remove mock data branches from get_child_categories method
  - Delete the entire `if self.mock_mode:` block that calls `MockDataService.get_child_categories()`

  - Keep only the real API implementation path
  - Ensure error handling propagates authentic errors without fallback
  - _Requirements: 1.1, 1.2, 1.3, 4.4, 4.5_

- [x] 1.4 Remove mock data branches from search_products method

  - Delete any `if self.mock_mode:` blocks in the search_products method
  - Keep only the real API implementation path
  - Ensure error handling propagates authentic errors without fallback
  - _Requirements: 1.1, 1.2, 1.3, 4.4, 4.5_



- [ ] 1.5 Remove mock data branches from remaining service methods
  - Remove mock mode logic from `get_products`, `get_products_details`, `get_affiliate_links`, `get_hotproducts`, and any other methods
  - Keep only real API implementation paths


  - Ensure all methods propagate authentic errors without fallback
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.4, 4.5_

- [ ] 2. Update Config class to enforce credential requirements
  - Modify configuration validation to fail fast when credentials are missing

  - Remove degraded mode logic that allows startup without valid credentials
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3, 7.4, 7.5_



- [ ] 2.1 Update Config.from_env() to fail fast on missing credentials
  - Remove fallback values like `'MISSING_APP_KEY'` and `'MISSING_APP_SECRET'`
  - Add immediate validation that raises `ConfigurationError` if `ALIEXPRESS_APP_KEY` is empty or missing


  - Add immediate validation that raises `ConfigurationError` if `ALIEXPRESS_APP_SECRET` is empty or missing
  - Include clear error messages with guidance on obtaining credentials
  - _Requirements: 7.1, 7.2, 7.5_



- [x] 2.2 Remove FORCE_MOCK_MODE from configuration logic


  - Ensure no code checks for `FORCE_MOCK_MODE` environment variable
  - Remove any configuration options related to mock mode
  - _Requirements: 2.1, 2.2, 2.3, 2.4_



- [ ] 3. Delete mock-related service files
  - Remove MockDataService and AliExpressServiceWithMock modules from the codebase
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [ ] 3.1 Delete MockDataService module
  - Delete the file `src/services/mock_data_service.py`
  - Delete compiled Python cache file `src/services/__pycache__/mock_data_service.cpython-312.pyc` if it exists
  - _Requirements: 3.1, 3.3_


- [ ] 3.2 Delete AliExpressServiceWithMock module
  - Delete the file `src/services/aliexpress_service_with_mock.py`
  - Delete compiled Python cache file `src/services/__pycache__/aliexpress_service_with_mock.cpython-312.pyc` if it exists
  - _Requirements: 3.2, 3.4_


- [ ] 4. Update API endpoint files to remove mock mode references
  - Modify all API endpoint files to use AliExpressService without mock mode
  - Remove mock mode status from API responses
  - _Requirements: 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_


- [ ] 4.1 Update API main.py to use AliExpressService
  - Change imports from `AliExpressServiceWithMock` to `AliExpressService`
  - Update service instantiation to use `AliExpressService(config)` without `force_mock` parameter
  - Remove any mock mode status from health check or service info responses


  - _Requirements: 2.5_

- [ ] 4.2 Update categories endpoint to remove mock mode references
  - Open `src/api/endpoints/categories.py`


  - Remove any `mock_mode` fields from response metadata
  - Ensure endpoint uses `AliExpressService` correctly
  - _Requirements: 2.5_



- [ ] 4.3 Update products endpoint to remove mock mode references
  - Open `src/api/endpoints/products.py`
  - Remove any `mock_mode` fields from response metadata


  - Ensure endpoint uses `AliExpressService` correctly
  - _Requirements: 2.5_



- [ ] 4.4 Update affiliate endpoint to remove mock mode references
  - Open `src/api/endpoints/affiliate.py`
  - Remove any `mock_mode` fields from response metadata
  - Ensure endpoint uses `AliExpressService` correctly


  - _Requirements: 2.5_

- [ ] 4.5 Update admin endpoint to remove mock mode references
  - Open `src/api/endpoints/admin.py`
  - Remove any `mock_mode` fields from response metadata or service info


  - Ensure endpoint uses `AliExpressService` correctly
  - _Requirements: 2.5_



- [ ] 5. Update test files to remove mock mode dependencies
  - Clean up all test files to remove mock mode setup and validation


  - Update tests to work with real API only
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_


- [ ] 5.1 Delete mock mode test files
  - Delete `test_mock_mode.py` from the root directory
  - Delete `test_live_mock_api.py` from the root directory
  - _Requirements: 3.5, 5.3_


- [ ] 5.2 Update test_api_endpoints.py
  - Remove `os.environ['FORCE_MOCK_MODE'] = 'false'` line
  - Remove mock mode checks like `if service_info.get('mock_mode'):`

  - Remove warnings about mock data responses
  - _Requirements: 5.1, 5.2, 5.4_



- [ ] 5.3 Update test_deployed_api.py
  - Remove mock mode status checks from response validation
  - Remove `Mock Mode:` and `Reason:` print statements


  - _Requirements: 5.1, 5.2, 5.4_

- [ ] 5.4 Update test_direct_import.py
  - Remove `os.environ['FORCE_MOCK_MODE'] = 'false'` line
  - Remove `print(f"   Mock mode: {service.mock_mode}")` line
  - Remove any imports of `AliExpressServiceWithMock`


  - _Requirements: 5.1, 5.2, 5.4_


- [ ] 5.5 Update test_local_service.py
  - Remove `os.environ['FORCE_MOCK_MODE'] = 'false'` line
  - Remove `force_mock=False` parameter from service initialization
  - Remove `print(f"   Mock mode: {service.mock_mode}")` line



  - Remove `if service.mock_mode:` check and warning
  - _Requirements: 5.1, 5.2, 5.4_

- [x] 5.6 Update test_real_api_e2e.py


  - Remove `os.environ['FORCE_MOCK_MODE'] = 'false'` line
  - Update comments to remove references to "no mock mode"
  - _Requirements: 5.1, 5.2, 5.4_



- [ ] 5.7 Update diagnostic scripts
  - Update `diagnose_credentials.py` to remove `os.environ["FORCE_MOCK_MODE"] = "false"` line
  - Update `diagnose_signature.py` to remove `os.environ['FORCE_MOCK_MODE'] = 'false'` line
  - _Requirements: 5.1, 5.2, 5.4_


- [ ] 6. Update environment configuration files
  - Remove mock mode variables from all environment templates
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


- [ ] 6.1 Update .env.example file
  - Remove any `FORCE_MOCK_MODE` variable definition
  - Remove any comments explaining mock mode
  - _Requirements: 9.1_


- [ ] 6.2 Update .env.secure.example file
  - Remove any `FORCE_MOCK_MODE` variable definition
  - Remove any comments explaining mock mode
  - _Requirements: 9.2_

- [ ] 6.3 Check and update .env.vercel file if it exists
  - Remove any `FORCE_MOCK_MODE` variable definition
  - _Requirements: 9.3_

- [ ] 7. Update documentation files
  - Remove all mock mode references from documentation
  - Update API response examples to remove mock mode fields
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 7.1 Update README.md
  - Remove all sections describing mock mode functionality
  - Remove mock mode from API response examples (remove `"mock_mode": true` fields)
  - Remove mock mode from troubleshooting section
  - Remove instructions on how to enable/disable mock mode
  - Update GPT integration documentation to remove mock mode references
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 7.2 Delete MOCK_MODE_IMPLEMENTATION.md
  - Delete the file `MOCK_MODE_IMPLEMENTATION.md` if it exists
  - _Requirements: 8.1, 8.4_

- [ ] 7.3 Update deployment documentation files
  - Check and update `DEPLOYMENT_INSTRUCTIONS.md`, `DEPLOY_RENDER_GUIDE.md`, and similar files
  - Remove any references to mock mode configuration
  - Remove `FORCE_MOCK_MODE` from environment variable lists
  - _Requirements: 8.3, 9.3, 9.4_

- [ ] 8. Verify and test the refactored codebase
  - Run comprehensive tests to ensure all mock mode logic is removed
  - Verify that the system works correctly with real API credentials
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8.1 Search codebase for remaining mock references
  - Use grep/search to find any remaining occurrences of "mock", "MOCK", "Mock" in Python files
  - Use grep/search to find any remaining occurrences of "FORCE_MOCK_MODE" in all files
  - Verify that only legitimate references remain (like in comments explaining what was removed)
  - _Requirements: 1.5, 2.4, 3.3, 3.4, 5.4_

- [ ] 8.2 Test service initialization with valid credentials
  - Create a test script that initializes `AliExpressService` with valid credentials
  - Verify that service initializes successfully without any mock mode warnings
  - Verify that `service.api` is properly initialized
  - _Requirements: 4.1, 4.2, 4.3, 7.1, 7.2_

- [ ] 8.3 Test service initialization without credentials
  - Create a test that attempts to initialize service without `ALIEXPRESS_APP_KEY`
  - Verify that `ConfigurationError` is raised with clear error message
  - Verify that error message includes guidance on obtaining credentials
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8.4 Test API endpoints return real data or authentic errors
  - Make test requests to each API endpoint
  - Verify responses do not contain `mock_mode` fields
  - Verify that errors return authentic error messages without fallback to mock data
  - _Requirements: 1.1, 1.4, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 8.5 Run full test suite
  - Execute `python -m pytest` to run all tests
  - Verify all tests pass with real API credentials
  - Fix any failing tests that were dependent on mock mode
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
