/**
 * Build system parameters required by AliExpress API
 * @param {string} method - AliExpress API method name
 * @returns {Object} - System parameters
 */
function buildSystemParameters(method) {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  
  return {
    app_key: process.env.ALIEXPRESS_APP_KEY,
    timestamp: timestamp,
    format: 'json',
    v: '2.0',
    sign_method: 'sha256',
    method: method
  };
}

/**
 * Merge user parameters with system parameters
 * @param {Object} userParams - Parameters from GPT request
 * @param {Object} systemParams - System parameters
 * @returns {Object} - Complete parameter set
 */
function mergeParameters(userParams, systemParams) {
  // Remove method from user params since it's in system params
  const { method, ...cleanUserParams } = userParams;
  
  return {
    ...systemParams,
    ...cleanUserParams
  };
}

/**
 * Validate required parameters for AliExpress API
 * @param {Object} params - Parameters to validate
 * @param {boolean} mockMode - Whether we're in mock mode
 * @returns {Object} - Validation result
 */
function validateParameters(params, mockMode = false) {
  const errors = [];
  
  // Check for required method parameter
  if (!params.method) {
    errors.push('method is required');
  }
  
  // Skip environment variable checks in mock mode
  if (!mockMode) {
    // Check for app_key (should be set from environment)
    if (!process.env.ALIEXPRESS_APP_KEY) {
      errors.push('ALIEXPRESS_APP_KEY environment variable is required');
    }
    
    // Check for app_secret (should be set from environment)
    if (!process.env.ALIEXPRESS_APP_SECRET) {
      errors.push('ALIEXPRESS_APP_SECRET environment variable is required');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

/**
 * Sanitize input parameters to prevent injection attacks
 * @param {Object} params - Parameters to sanitize
 * @returns {Object} - Sanitized parameters
 */
function sanitizeParameters(params) {
  const sanitized = {};
  
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === 'string') {
      // Remove potentially dangerous characters
      sanitized[key] = value.replace(/[<>\"'&]/g, '');
    } else if (typeof value === 'number') {
      sanitized[key] = value;
    } else if (value !== null && value !== undefined) {
      sanitized[key] = String(value);
    }
  }
  
  return sanitized;
}

module.exports = {
  buildSystemParameters,
  mergeParameters,
  validateParameters,
  sanitizeParameters
};