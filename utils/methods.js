/**
 * AliExpress API method configurations
 */
const METHOD_CONFIGS = {
  'aliexpress.affiliate.product.query': {
    description: 'Search for affiliate products',
    required_params: ['keywords'],
    optional_params: ['category_ids', 'page_no', 'page_size', 'target_currency', 'target_language', 'sort'],
    defaults: {
      page_no: 1,
      page_size: 20,
      target_currency: 'USD',
      target_language: 'EN'
    }
  },
  'aliexpress.affiliate.category.get': {
    description: 'Get affiliate categories',
    required_params: [],
    optional_params: ['app_signature'],
    defaults: {}
  },
  'aliexpress.affiliate.link.generate': {
    description: 'Generate affiliate tracking links',
    required_params: ['promotion_link_type', 'source_values'],
    optional_params: ['tracking_id'],
    defaults: {
      promotion_link_type: 0
    }
  },
  'aliexpress.affiliate.hotproduct.query': {
    description: 'Query hot affiliate products',
    required_params: [],
    optional_params: ['category_ids', 'page_no', 'page_size', 'target_currency', 'target_language', 'sort'],
    defaults: {
      page_no: 1,
      page_size: 20,
      target_currency: 'USD',
      target_language: 'EN'
    }
  },
  'aliexpress.affiliate.order.get': {
    description: 'Get affiliate order information',
    required_params: ['order_ids'],
    optional_params: ['fields'],
    defaults: {}
  }
};

/**
 * Get method configuration
 * @param {string} method - AliExpress API method name
 * @returns {Object|null} - Method configuration or null if not supported
 */
function getMethodConfig(method) {
  return METHOD_CONFIGS[method] || null;
}

/**
 * Get all supported methods
 * @returns {Array<string>} - Array of supported method names
 */
function getSupportedMethods() {
  return Object.keys(METHOD_CONFIGS);
}

/**
 * Apply default parameters for a method
 * @param {string} method - AliExpress API method name
 * @param {Object} params - User provided parameters
 * @returns {Object} - Parameters with defaults applied
 */
function applyMethodDefaults(method, params) {
  const config = getMethodConfig(method);
  if (!config) {
    return params;
  }
  
  return {
    ...config.defaults,
    ...params
  };
}

/**
 * Validate method-specific parameters
 * @param {string} method - AliExpress API method name
 * @param {Object} params - Parameters to validate
 * @returns {Object} - Validation result
 */
function validateMethodParameters(method, params) {
  const config = getMethodConfig(method);
  const errors = [];
  
  if (!config) {
    errors.push(`Unsupported method: ${method}`);
    return { isValid: false, errors };
  }
  
  // Check required parameters
  config.required_params.forEach(param => {
    if (!params[param] || params[param] === '') {
      errors.push(`Required parameter missing: ${param}`);
    }
  });
  
  // Validate specific parameter formats
  if (params.page_no && (isNaN(params.page_no) || params.page_no < 1)) {
    errors.push('page_no must be a positive integer');
  }
  
  if (params.page_size && (isNaN(params.page_size) || params.page_size < 1 || params.page_size > 50)) {
    errors.push('page_size must be between 1 and 50');
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

module.exports = {
  getMethodConfig,
  getSupportedMethods,
  applyMethodDefaults,
  validateMethodParameters,
  METHOD_CONFIGS
};