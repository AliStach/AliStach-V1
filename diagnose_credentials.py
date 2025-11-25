"""Diagnose AliExpress API credential issues."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config

def main():
    """Diagnose credential configuration."""
    print("="*80)
    print("ALIEXPRESS API CREDENTIALS DIAGNOSTIC")
    print("="*80)
    
    try:
        config = Config.from_env()
        
        print("\n📋 Configuration Loaded:")
        print(f"   App Key: {config.app_key}")
        print(f"   App Key Length: {len(config.app_key)} characters")
        print(f"   App Key Type: {type(config.app_key)}")
        print(f"   App Secret: {'*' * (len(config.app_secret) - 4)}{config.app_secret[-4:]}")
        print(f"   App Secret Length: {len(config.app_secret)} characters")
        print(f"   App Secret Type: {type(config.app_secret)}")
        print(f"   Tracking ID: {config.tracking_id}")
        print(f"   Language: {config.language}")
        print(f"   Currency: {config.currency}")
        
        print("\n🔍 Validation Checks:")
        
        # Check if credentials look valid
        issues = []
        
        if not config.app_key or config.app_key == "your_app_key_here":
            issues.append("❌ APP_KEY appears to be placeholder/invalid")
        elif len(config.app_key) < 5:
            issues.append("⚠️  APP_KEY seems too short")
        else:
            print("   ✅ APP_KEY format looks reasonable")
        
        if not config.app_secret or config.app_secret == "your_app_secret_here":
            issues.append("❌ APP_SECRET appears to be placeholder/invalid")
        elif len(config.app_secret) < 10:
            issues.append("⚠️  APP_SECRET seems too short")
        else:
            print("   ✅ APP_SECRET format looks reasonable")
        
        if config.tracking_id == "default":
            issues.append("⚠️  TRACKING_ID is set to 'default' - should be your affiliate tracking ID")
        else:
            print(f"   ✅ TRACKING_ID is set: {config.tracking_id}")
        
        # Try to initialize the API
        print("\n🔌 Testing API Initialization:")
        try:
            from aliexpress_api import AliexpressApi, models
            
            api = AliexpressApi(
                key=config.app_key,
                secret=config.app_secret,
                language=getattr(models.Language, config.language),
                currency=getattr(models.Currency, config.currency),
                tracking_id=config.tracking_id
            )
            print("   ✅ API client initialized successfully")
            
            # Try a simple API call
            print("\n🧪 Testing API Call (get_parent_categories):")
            try:
                categories = api.get_parent_categories()
                if categories:
                    print(f"   ✅ SUCCESS! Retrieved {len(categories)} categories")
                    print(f"\n   Sample categories:")
                    for i, cat in enumerate(categories[:3], 1):
                        print(f"   {i}. {cat.category_name} (ID: {cat.category_id})")
                else:
                    print("   ⚠️  API call succeeded but returned no categories")
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ API call failed: {error_msg}")
                
                # Analyze the error
                if "signature" in error_msg.lower():
                    issues.append("❌ SIGNATURE ERROR - APP_SECRET is likely incorrect")
                    print("\n   💡 Signature errors usually mean:")
                    print("      1. APP_SECRET is wrong or has extra spaces")
                    print("      2. APP_KEY doesn't match APP_SECRET")
                    print("      3. Credentials are from wrong environment (test vs production)")
                elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                    issues.append("❌ INVALID KEY ERROR - APP_KEY is likely incorrect")
                    print("\n   💡 Invalid key errors usually mean:")
                    print("      1. APP_KEY is wrong or expired")
                    print("      2. API access not approved yet")
                    print("      3. Using test credentials in production")
                elif "permission" in error_msg.lower():
                    issues.append("⚠️  PERMISSION ERROR - API access may not be fully approved")
                    print("\n   💡 Permission errors usually mean:")
                    print("      1. API access pending approval")
                    print("      2. Specific endpoint requires additional permissions")
                    print("      3. Account not fully activated")
                else:
                    issues.append(f"❌ UNKNOWN ERROR: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ Failed to initialize API client: {e}")
            issues.append(f"❌ API initialization failed: {str(e)}")
        
        # Summary
        print("\n" + "="*80)
        print("DIAGNOSTIC SUMMARY")
        print("="*80)
        
        if not issues:
            print("\n✅ ALL CHECKS PASSED!")
            print("   Your AliExpress API credentials appear to be valid and working.")
        else:
            print(f"\n⚠️  FOUND {len(issues)} ISSUE(S):")
            for issue in issues:
                print(f"   {issue}")
            
            print("\n📝 RECOMMENDED ACTIONS:")
            print("   1. Verify your credentials at: https://portals.aliexpress.com/")
            print("   2. Check that you're using PRODUCTION credentials (not test/sandbox)")
            print("   3. Ensure APP_KEY and APP_SECRET match and have no extra spaces")
            print("   4. Confirm your API access has been fully approved")
            print("   5. Update Vercel environment variables if credentials changed:")
            print("      vercel env rm ALIEXPRESS_APP_KEY production")
            print("      vercel env rm ALIEXPRESS_APP_SECRET production")
            print("      vercel env add ALIEXPRESS_APP_KEY production")
            print("      vercel env add ALIEXPRESS_APP_SECRET production")
            print("      vercel --prod")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print("\nCould not load configuration. Check your .env file.")
        return False
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
