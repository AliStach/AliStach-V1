/**
 * Mock AliExpress API responses for testing without real credentials
 */

const MOCK_PRODUCT_RESPONSE = {
  "aliexpress_affiliate_product_query_response": {
    "resp_result": {
      "result": {
        "products": [
          {
            "product_id": "1005004123456789",
            "product_title": "Wireless Bluetooth Headphones - Premium Sound Quality",
            "product_main_image_url": "https://ae01.alicdn.com/kf/example1.jpg",
            "product_video_url": "",
            "product_small_image_urls": [
              "https://ae01.alicdn.com/kf/example1_small.jpg",
              "https://ae01.alicdn.com/kf/example2_small.jpg"
            ],
            "app_sale_price": "29.99",
            "app_sale_price_currency": "USD",
            "original_price": "59.99",
            "original_price_currency": "USD",
            "discount": "50%",
            "evaluate_rate": "98.5%",
            "30days_commission": "8.99",
            "volume": 15420,
            "product_detail_url": "https://www.aliexpress.com/item/1005004123456789.html",
            "promotion_link": "https://s.click.aliexpress.com/e/_example_link",
            "shop_id": "912345678",
            "shop_url": "https://example.aliexpress.com/store/912345678",
            "commission_rate": "30%",
            "hot_product_commission_rate": "35%",
            "relevant_market_commission_rate": "30%",
            "lastest_volume": 1250,
            "category_id": 509,
            "category_name": "Consumer Electronics"
          },
          {
            "product_id": "1005004987654321",
            "product_title": "Gaming Headset with Microphone - RGB LED Lights",
            "product_main_image_url": "https://ae01.alicdn.com/kf/example2.jpg",
            "product_video_url": "https://video.aliexpress-media.com/example.mp4",
            "product_small_image_urls": [
              "https://ae01.alicdn.com/kf/example3_small.jpg",
              "https://ae01.alicdn.com/kf/example4_small.jpg"
            ],
            "app_sale_price": "45.99",
            "app_sale_price_currency": "USD",
            "original_price": "89.99",
            "original_price_currency": "USD",
            "discount": "49%",
            "evaluate_rate": "96.8%",
            "30days_commission": "13.80",
            "volume": 8750,
            "product_detail_url": "https://www.aliexpress.com/item/1005004987654321.html",
            "promotion_link": "https://s.click.aliexpress.com/e/_example_link2",
            "shop_id": "912345679",
            "shop_url": "https://example2.aliexpress.com/store/912345679",
            "commission_rate": "30%",
            "hot_product_commission_rate": "35%",
            "relevant_market_commission_rate": "30%",
            "lastest_volume": 890,
            "category_id": 708,
            "category_name": "Computer & Office"
          },
          {
            "product_id": "1005005111222333",
            "product_title": "Noise Cancelling Wireless Earbuds - Touch Control",
            "product_main_image_url": "https://ae01.alicdn.com/kf/example3.jpg",
            "product_video_url": "",
            "product_small_image_urls": [
              "https://ae01.alicdn.com/kf/example5_small.jpg",
              "https://ae01.alicdn.com/kf/example6_small.jpg"
            ],
            "app_sale_price": "19.99",
            "app_sale_price_currency": "USD",
            "original_price": "39.99",
            "original_price_currency": "USD",
            "discount": "50%",
            "evaluate_rate": "94.2%",
            "30days_commission": "5.99",
            "volume": 25680,
            "product_detail_url": "https://www.aliexpress.com/item/1005005111222333.html",
            "promotion_link": "https://s.click.aliexpress.com/e/_example_link3",
            "shop_id": "912345680",
            "shop_url": "https://example3.aliexpress.com/store/912345680",
            "commission_rate": "30%",
            "hot_product_commission_rate": "35%",
            "relevant_market_commission_rate": "30%",
            "lastest_volume": 2150,
            "category_id": 509,
            "category_name": "Consumer Electronics"
          }
        ],
        "total_record_count": 15420,
        "current_page_no": 1,
        "current_record_count": 3
      },
      "resp_code": 200,
      "resp_msg": "success"
    },
    "request_id": "mock_request_" + Date.now()
  }
};

const MOCK_CATEGORY_RESPONSE = {
  "aliexpress_affiliate_category_get_response": {
    "resp_result": {
      "result": {
        "categories": [
          {
            "category_id": 509,
            "category_name": "Consumer Electronics",
            "parent_category_id": 0
          },
          {
            "category_id": 708,
            "category_name": "Computer & Office",
            "parent_category_id": 0
          },
          {
            "category_id": 1420,
            "category_name": "Automobiles & Motorcycles",
            "parent_category_id": 0
          },
          {
            "category_id": 1501,
            "category_name": "Jewelry & Accessories",
            "parent_category_id": 0
          }
        ]
      },
      "resp_code": 200,
      "resp_msg": "success"
    },
    "request_id": "mock_request_" + Date.now()
  }
};

const MOCK_HOT_PRODUCTS_RESPONSE = {
  "aliexpress_affiliate_hotproduct_query_response": {
    "resp_result": {
      "result": {
        "products": [
          {
            "product_id": "1005006789012345",
            "product_title": "🔥 HOT SALE - Wireless Charging Pad Fast Charger",
            "product_main_image_url": "https://ae01.alicdn.com/kf/hot1.jpg",
            "app_sale_price": "12.99",
            "app_sale_price_currency": "USD",
            "original_price": "25.99",
            "original_price_currency": "USD",
            "discount": "50%",
            "evaluate_rate": "99.1%",
            "30days_commission": "3.90",
            "volume": 45230,
            "product_detail_url": "https://www.aliexpress.com/item/1005006789012345.html",
            "promotion_link": "https://s.click.aliexpress.com/e/_hot_link1",
            "commission_rate": "30%",
            "lastest_volume": 3420,
            "category_id": 509
          },
          {
            "product_id": "1005006789012346",
            "product_title": "🔥 TRENDING - Smart Watch Fitness Tracker",
            "product_main_image_url": "https://ae01.alicdn.com/kf/hot2.jpg",
            "app_sale_price": "24.99",
            "app_sale_price_currency": "USD",
            "original_price": "49.99",
            "original_price_currency": "USD",
            "discount": "50%",
            "evaluate_rate": "97.8%",
            "30days_commission": "7.50",
            "volume": 32150,
            "product_detail_url": "https://www.aliexpress.com/item/1005006789012346.html",
            "promotion_link": "https://s.click.aliexpress.com/e/_hot_link2",
            "commission_rate": "30%",
            "lastest_volume": 2890,
            "category_id": 509
          }
        ],
        "total_record_count": 500,
        "current_page_no": 1,
        "current_record_count": 2
      },
      "resp_code": 200,
      "resp_msg": "success"
    },
    "request_id": "mock_request_" + Date.now()
  }
};

/**
 * Generate mock response based on method
 * @param {string} method - AliExpress API method
 * @param {Object} params - Request parameters
 * @returns {Object} - Mock response
 */
function generateMockResponse(method, params) {
  // Add some delay to simulate network request
  const delay = Math.random() * 500 + 200; // 200-700ms delay
  
  return new Promise((resolve) => {
    setTimeout(() => {
      switch (method) {
        case 'aliexpress.affiliate.product.query':
          // Customize response based on keywords
          const response = JSON.parse(JSON.stringify(MOCK_PRODUCT_RESPONSE));
          if (params.keywords) {
            response.aliexpress_affiliate_product_query_response.resp_result.result.products.forEach(product => {
              product.product_title = `${params.keywords} - ${product.product_title}`;
            });
          }
          resolve(response);
          break;
          
        case 'aliexpress.affiliate.category.get':
          resolve(MOCK_CATEGORY_RESPONSE);
          break;
          
        case 'aliexpress.affiliate.hotproduct.query':
          resolve(MOCK_HOT_PRODUCTS_RESPONSE);
          break;
          
        case 'aliexpress.affiliate.link.generate':
          resolve({
            "aliexpress_affiliate_link_generate_response": {
              "resp_result": {
                "result": {
                  "promotion_links": [
                    {
                      "promotion_link": "https://s.click.aliexpress.com/e/_mock_generated_link"
                    }
                  ]
                },
                "resp_code": 200,
                "resp_msg": "success"
              },
              "request_id": "mock_request_" + Date.now()
            }
          });
          break;
          
        case 'aliexpress.affiliate.order.get':
          resolve({
            "aliexpress_affiliate_order_get_response": {
              "resp_result": {
                "result": {
                  "orders": [
                    {
                      "order_id": "123456789012345",
                      "order_status": "Completed",
                      "commission_rate": "30%",
                      "commission_amount": "8.99",
                      "order_amount": "29.99",
                      "currency": "USD",
                      "created_time": new Date().toISOString()
                    }
                  ]
                },
                "resp_code": 200,
                "resp_msg": "success"
              },
              "request_id": "mock_request_" + Date.now()
            }
          });
          break;
          
        default:
          resolve({
            "error_response": {
              "code": "INVALID_METHOD",
              "msg": `Method ${method} not supported in mock mode`
            }
          });
      }
    }, delay);
  });
}

/**
 * Check if we should use mock mode
 * @returns {boolean} - True if mock mode should be used
 */
function shouldUseMockMode() {
  // Force mock mode if FORCE_MOCK_MODE is set
  if (process.env.FORCE_MOCK_MODE === 'true') {
    return true;
  }
  
  // Use mock mode if credentials are not set or are placeholder values
  const appKey = process.env.ALIEXPRESS_APP_KEY;
  const appSecret = process.env.ALIEXPRESS_APP_SECRET;
  
  return !appKey || 
         !appSecret || 
         appKey === 'your_app_key_here' || 
         appSecret === 'your_app_secret_here' ||
         appKey.length < 8 ||
         appSecret.length < 16;
}

module.exports = {
  generateMockResponse,
  shouldUseMockMode,
  MOCK_PRODUCT_RESPONSE,
  MOCK_CATEGORY_RESPONSE,
  MOCK_HOT_PRODUCTS_RESPONSE
};