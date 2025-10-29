const { createErrorResponse } = require('../utils/response');

/**
 * Optional API token validation middleware
 */
function validateApiToken(req, res, next) {
  const startTime = Date.now();
  
  // Skip token validation if no token is configured
  if (!process.env.API_TOKEN) {
    return next();
  }
  
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.startsWith('Bearer ') 
    ? authHeader.substring(7) 
    : req.headers['x-api-key'] || req.query.token;
  
  if (!token) {
    return res.status(401).json(
      createErrorResponse(
        'MISSING_TOKEN',
        'API token is required',
        null,
        startTime
      )
    );
  }
  
  if (token !== process.env.API_TOKEN) {
    return res.status(401).json(
      createErrorResponse(
        'INVALID_TOKEN',
        'Invalid API token',
        null,
        startTime
      )
    );
  }
  
  next();
}

/**
 * Request logging middleware
 */
function logRequest(req, res, next) {
  const startTime = Date.now();
  const timestamp = new Date().toISOString();
  const ip = req.ip || req.connection.remoteAddress;
  const userAgent = req.headers['user-agent'] || 'Unknown';
  
  // Log request (excluding sensitive data)
  const logData = {
    timestamp,
    method: req.method,
    url: req.url,
    ip,
    userAgent,
    bodySize: JSON.stringify(req.body || {}).length,
    hasMethod: !!req.body?.method,
    aliexpressMethod: req.body?.method || null
  };
  
  console.log('Request:', JSON.stringify(logData));
  
  // Log response when it finishes
  const originalSend = res.send;
  res.send = function(data) {
    const responseTime = Date.now() - startTime;
    const responseSize = typeof data === 'string' ? data.length : JSON.stringify(data).length;
    
    const responseLog = {
      timestamp: new Date().toISOString(),
      ip,
      statusCode: res.statusCode,
      responseTime,
      responseSize,
      success: res.statusCode < 400
    };
    
    console.log('Response:', JSON.stringify(responseLog));
    
    originalSend.call(this, data);
  };
  
  next();
}

/**
 * Request size limit middleware
 */
function limitRequestSize(maxSize = 1024 * 1024) { // 1MB default
  return (req, res, next) => {
    const startTime = Date.now();
    
    if (req.headers['content-length'] && parseInt(req.headers['content-length']) > maxSize) {
      return res.status(413).json(
        createErrorResponse(
          'REQUEST_TOO_LARGE',
          `Request size exceeds limit of ${maxSize} bytes`,
          null,
          startTime
        )
      );
    }
    
    next();
  };
}

module.exports = {
  validateApiToken,
  logRequest,
  limitRequestSize
};