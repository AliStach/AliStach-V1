const crypto = require('crypto');

/**
 * Generate SHA256 signature for AliExpress API
 * @param {Object} params - All parameters including system and user params
 * @param {string} appSecret - AliExpress app secret
 * @returns {string} - Hexadecimal signature
 */
function generateSignature(params, appSecret) {
  if (!appSecret) {
    throw new Error('App secret is required for signature generation');
  }
  
  // Remove sign parameter if it exists
  const { sign, ...paramsToSign } = params;
  
  // Sort parameters alphabetically by key
  const sortedKeys = Object.keys(paramsToSign).sort();
  
  // Build parameter string according to AliExpress format
  let paramString = '';
  sortedKeys.forEach(key => {
    const value = paramsToSign[key];
    if (value !== undefined && value !== null && value !== '') {
      paramString += key + value;
    }
  });
  
  // Add app secret to the end (AliExpress specific requirement)
  paramString += appSecret;
  
  // Generate SHA256 hash and return uppercase hex
  const hash = crypto.createHash('sha256');
  hash.update(paramString, 'utf8');
  return hash.digest('hex').toUpperCase();
}

/**
 * Sort parameters alphabetically for consistent signature generation
 * @param {Object} params - Parameters to sort
 * @returns {Object} - Sorted parameters
 */
function sortParameters(params) {
  const sortedKeys = Object.keys(params).sort();
  const sortedParams = {};
  
  sortedKeys.forEach(key => {
    sortedParams[key] = params[key];
  });
  
  return sortedParams;
}

module.exports = {
  generateSignature,
  sortParameters
};