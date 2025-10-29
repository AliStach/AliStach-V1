const { validateParameters, sanitizeParameters } = require('../utils/parameters');
const { createErrorResponse } = require('../utils/response');
const { getSupportedMethods, validateMethodParameters } = require('../utils/methods');

/**
 * Middleware to validate and sanitize incoming requests
 */
function validateRequest(req, res, next) {
  const startTime = Date.now();
  
  try {
    // Sanitize input parameters
    req.body = sanitizeParameters(req.body || {});
    
    // Validate required parameters
    const validation = validateParameters(req.body);
    
    if (!validation.isValid) {
      return res.status(400).json(
        createErrorResponse(
          'INVALID_PARAMETERS',
          'Request validation failed',
          { errors: validation.errors },
          startTime
        )
      );
    }
    
    // Check for supported AliExpress methods
    const supportedMethods = getSupportedMethods();
    
    if (req.body.method && !supportedMethods.includes(req.body.method)) {
      return res.status(400).json(
        createErrorResponse(
          'UNSUPPORTED_METHOD',
          `Method '${req.body.method}' is not supported`,
          { supported_methods: supportedMethods },
          startTime
        )
      );
    }
    
    // Validate method-specific parameters
    if (req.body.method) {
      const methodValidation = validateMethodParameters(req.body.method, req.body);
      if (!methodValidation.isValid) {
        return res.status(400).json(
          createErrorResponse(
            'INVALID_METHOD_PARAMETERS',
            'Method-specific parameter validation failed',
            { errors: methodValidation.errors },
            startTime
          )
        );
      }
    }
    
    // Add request start time for performance tracking
    req.startTime = startTime;
    
    next();
  } catch (error) {
    console.error('Validation middleware error:', error);
    return res.status(500).json(
      createErrorResponse(
        'VALIDATION_ERROR',
        'Request validation failed',
        { error: error.message },
        startTime
      )
    );
  }
}

/**
 * Middleware to validate environment variables
 */
function validateEnvironment(req, res, next) {
  const startTime = Date.now();
  
  if (!process.env.ALIEXPRESS_APP_KEY) {
    return res.status(500).json(
      createErrorResponse(
        'CONFIGURATION_ERROR',
        'AliExpress app key not configured',
        null,
        startTime
      )
    );
  }
  
  if (!process.env.ALIEXPRESS_APP_SECRET) {
    return res.status(500).json(
      createErrorResponse(
        'CONFIGURATION_ERROR',
        'AliExpress app secret not configured',
        null,
        startTime
      )
    );
  }
  
  next();
}

module.exports = {
  validateRequest,
  validateEnvironment
};