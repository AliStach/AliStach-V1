const https = require('https');
const querystring = require('querystring');
const { generateSignature } = require('../utils/signature');
const { buildSystemParameters, mergeParameters } = require('../utils/parameters');
const { formatAliExpressResponse, createErrorResponse } = require('../utils/response');
const { applyMethodDefaults } = require('../utils/methods');
const { generateMockResponse, shouldUseMockMode } = require('../utils/mock-data');

/**
 * Main AliExpress API proxy handler
 */
async function handleAliExpressRequest(req, res) {
  const startTime = req.startTime || Date.now();
  
  console.log('🔄 Processing AliExpress request:', {
    method: req.body.method,
    keywords: req.body.keywords,
    mockMode: shouldUseMockMode()
  });
  
  try {
    // Check if we should use mock mode
    if (shouldUseMockMode()) {
      console.log('🧪 Using mock mode - generating mock response');
      
      // Apply method-specific defaults for mock response
      const paramsWithDefaults = applyMethodDefaults(req.body.method, req.body);
      console.log('📝 Parameters with defaults:', paramsWithDefaults);
      
      // Generate mock response
      const mockResponse = await generateMockResponse(req.body.method, paramsWithDefaults);
      console.log('✅ Mock response generated successfully');
      
      // Add mock indicator to response
      const formattedResponse = formatAliExpressResponse(mockResponse, startTime);
      formattedResponse.metadata.mock_mode = true;
      formattedResponse.metadata.note = "This is mock data. Set real AliExpress credentials to get live data.";
      
      console.log('📤 Sending mock response to GPT');
      res.status(200).json(formattedResponse);
      return;
    }
    
    // Real AliExpress API mode
    console.log('🔗 Using real AliExpress API');
    
    try {
      // Apply method-specific defaults
      const paramsWithDefaults = applyMethodDefaults(req.body.method, req.body);
      console.log('📝 Parameters with defaults:', paramsWithDefaults);
      
      // Build system parameters
      const systemParams = buildSystemParameters(req.body.method);
      console.log('🔧 System parameters:', systemParams);
      
      // Merge with user parameters (with defaults applied)
      const allParams = mergeParameters(paramsWithDefaults, systemParams);
      
      // Generate signature
      const signature = generateSignature(allParams, process.env.ALIEXPRESS_APP_SECRET);
      console.log('🔐 Signature generated');
      
      // Add signature to parameters
      const finalParams = {
        ...allParams,
        sign: signature
      };
      
      // Convert to query string
      const queryString = querystring.stringify(finalParams);
      console.log('🌐 Making request to AliExpress API');
      
      // Make request to AliExpress API
      const aliexpressResponse = await makeAliExpressRequest(queryString);
      console.log('✅ AliExpress API response received');
      
      // Format and return response
      const formattedResponse = formatAliExpressResponse(aliexpressResponse, startTime);
      
      // Set appropriate status code
      const statusCode = formattedResponse.success ? 200 : 400;
      console.log('📤 Sending real API response to GPT');
      res.status(statusCode).json(formattedResponse);
      
    } catch (apiError) {
      console.error('❌ Real AliExpress API failed, falling back to mock mode:', apiError.message);
      
      // Fallback to mock mode if real API fails
      const paramsWithDefaults = applyMethodDefaults(req.body.method, req.body);
      const mockResponse = await generateMockResponse(req.body.method, paramsWithDefaults);
      const formattedResponse = formatAliExpressResponse(mockResponse, startTime);
      formattedResponse.metadata.mock_mode = true;
      formattedResponse.metadata.note = "Fallback to mock data due to AliExpress API error.";
      formattedResponse.metadata.api_error = apiError.message;
      
      console.log('📤 Sending fallback mock response to GPT');
      res.status(200).json(formattedResponse);
    }
    
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