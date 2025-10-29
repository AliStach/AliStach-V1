const https = require('https');
const querystring = require('querystring');
const { generateSignature } = require('../utils/signature');
const { buildSystemParameters, mergeParameters } = require('../utils/parameters');
const { formatAliExpressResponse, createErrorResponse } = require('../utils/response');
const { applyMethodDefaults } = require('../utils/methods');

/**
 * Main AliExpress API proxy handler
 */
async function handleAliExpressRequest(req, res) {
  const startTime = req.startTime || Date.now();
  
  try {
    // Apply method-specific defaults
    const paramsWithDefaults = applyMethodDefaults(req.body.method, req.body);
    
    // Build system parameters
    const systemParams = buildSystemParameters(req.body.method);
    
    // Merge with user parameters (with defaults applied)
    const allParams = mergeParameters(paramsWithDefaults, systemParams);
    
    // Generate signature
    const signature = generateSignature(allParams, process.env.ALIEXPRESS_APP_SECRET);
    
    // Add signature to parameters
    const finalParams = {
      ...allParams,
      sign: signature
    };
    
    // Convert to query string
    const queryString = querystring.stringify(finalParams);
    
    // Make request to AliExpress API
    const aliexpressResponse = await makeAliExpressRequest(queryString);
    
    // Format and return response
    const formattedResponse = formatAliExpressResponse(aliexpressResponse, startTime);
    
    // Set appropriate status code
    const statusCode = formattedResponse.success ? 200 : 400;
    res.status(statusCode).json(formattedResponse);
    
  } catch (error) {
    console.error('AliExpress API request error:', error);
    
    const errorResponse = createErrorResponse(
      'PROXY_ERROR',
      'Failed to process AliExpress API request',
      { error: error.message },
      startTime
    );
    
    res.status(500).json(errorResponse);
  }
}

/**
 * Make HTTP request to AliExpress API
 * @param {string} queryString - URL encoded parameters
 * @returns {Promise<Object>} - AliExpress API response
 */
function makeAliExpressRequest(queryString) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api-sg.aliexpress.com',
      path: '/sync?' + queryString,
      method: 'GET',
      headers: {
        'User-Agent': 'AliExpress-API-Proxy/1.0',
        'Accept': 'application/json'
      },
      timeout: 30000 // 30 second timeout
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonResponse = JSON.parse(data);
          resolve(jsonResponse);
        } catch (parseError) {
          reject(new Error(`Failed to parse AliExpress response: ${parseError.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(new Error(`AliExpress API request failed: ${error.message}`));
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('AliExpress API request timed out'));
    });
    
    req.end();
  });
}

module.exports = {
  handleAliExpressRequest
};