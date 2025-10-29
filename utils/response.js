const { v4: uuidv4 } = require('uuid');

/**
 * Create standardized success response
 * @param {any} data - Response data from AliExpress API
 * @param {number} startTime - Request start time for performance tracking
 * @returns {Object} - Formatted response
 */
function createSuccessResponse(data, startTime = Date.now()) {
  return {
    success: true,
    data: data,
    metadata: {
      request_id: uuidv4(),
      timestamp: new Date().toISOString(),
      processing_time_ms: Date.now() - startTime
    }
  };
}

/**
 * Create standardized error response
 * @param {string} code - Error code
 * @param {string} message - Error message
 * @param {any} details - Additional error details
 * @param {number} startTime - Request start time for performance tracking
 * @returns {Object} - Formatted error response
 */
function createErrorResponse(code, message, details = null, startTime = Date.now()) {
  const response = {
    success: false,
    error: {
      code: code,
      message: message
    },
    metadata: {
      request_id: uuidv4(),
      timestamp: new Date().toISOString(),
      processing_time_ms: Date.now() - startTime
    }
  };
  
  if (details) {
    response.error.details = details;
  }
  
  return response;
}

/**
 * Format AliExpress API response for GPT consumption
 * @param {any} aliexpressResponse - Raw response from AliExpress API
 * @param {number} startTime - Request start time
 * @returns {Object} - Formatted response
 */
function formatAliExpressResponse(aliexpressResponse, startTime = Date.now()) {
  try {
    // Check if AliExpress returned an error
    if (aliexpressResponse.error_response) {
      return createErrorResponse(
        'ALIEXPRESS_API_ERROR',
        aliexpressResponse.error_response.msg || 'AliExpress API error',
        aliexpressResponse.error_response,
        startTime
      );
    }
    
    // Return successful response with AliExpress data
    return createSuccessResponse(aliexpressResponse, startTime);
  } catch (error) {
    return createErrorResponse(
      'RESPONSE_FORMAT_ERROR',
      'Failed to format AliExpress response',
      { original_error: error.message },
      startTime
    );
  }
}

module.exports = {
  createSuccessResponse,
  createErrorResponse,
  formatAliExpressResponse
};