const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');

const { handleAliExpressRequest } = require('./aliexpress');
const { validateRequest, validateEnvironment } = require('../middleware/validation');
const { validateApiToken, logRequest, limitRequestSize } = require('../middleware/security');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// CORS configuration for GPT access
app.use(cors({
  origin: [
    'https://chat.openai.com',
    'https://chatgpt.com',
    'https://platform.openai.com',
    /^https:\/\/.*\.openai\.com$/,
    // Allow localhost for development
    /^http:\/\/localhost:\d+$/,
    /^http:\/\/127\.0\.0\.1:\d+$/
  ],
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key'],
  credentials: false,
  maxAge: 86400 // 24 hours
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    success: false,
    error: {
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Too many requests, please try again later'
    }
  }
});
app.use(limiter);

// Request size limiting
app.use(limitRequestSize(1024 * 1024)); // 1MB limit

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use(logRequest);

// Enhanced health check endpoint
app.get('/health', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Check environment configuration
    const configStatus = {
      app_key_configured: !!process.env.ALIEXPRESS_APP_KEY,
      app_secret_configured: !!process.env.ALIEXPRESS_APP_SECRET,
      api_token_configured: !!process.env.API_TOKEN
    };
    
    // Basic memory usage
    const memoryUsage = process.memoryUsage();
    
    // System uptime
    const uptime = process.uptime();
    
    const healthData = {
      success: true,
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      uptime_seconds: Math.floor(uptime),
      memory_usage: {
        rss_mb: Math.round(memoryUsage.rss / 1024 / 1024),
        heap_used_mb: Math.round(memoryUsage.heapUsed / 1024 / 1024),
        heap_total_mb: Math.round(memoryUsage.heapTotal / 1024 / 1024)
      },
      configuration: configStatus,
      response_time_ms: Date.now() - startTime
    };
    
    res.json(healthData);
  } catch (error) {
    res.status(500).json({
      success: false,
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
      response_time_ms: Date.now() - startTime
    });
  }
});

// Load OpenAPI specification
let openApiSpec;
try {
  const specPath = path.join(__dirname, '..', 'docs', 'openapi.json');
  openApiSpec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
} catch (error) {
  console.warn('Could not load OpenAPI specification:', error.message);
  openApiSpec = {
    openapi: '3.1.0',
    info: {
      title: 'AliExpress API Proxy',
      version: '1.0.0',
      description: 'OpenAPI specification not available'
    },
    paths: {}
  };
}

// Serve OpenAPI documentation
app.use('/docs', swaggerUi.serve, swaggerUi.setup(openApiSpec, {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'AliExpress API Proxy Documentation',
  swaggerOptions: {
    displayRequestDuration: true,
    tryItOutEnabled: true,
    filter: true,
    showExtensions: true,
    showCommonExtensions: true
  }
}));

// Serve raw OpenAPI spec
app.get('/openapi.json', (req, res) => {
  res.json(openApiSpec);
});

// Main AliExpress API proxy endpoint
app.post('/api/aliexpress', 
  validateEnvironment,
  validateApiToken,
  validateRequest,
  handleAliExpressRequest
);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: 'Endpoint not found'
    }
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Internal server error'
    }
  });
});

app.listen(PORT, () => {
  console.log(`AliExpress API Proxy running on port ${PORT}`);
});

module.exports = app;