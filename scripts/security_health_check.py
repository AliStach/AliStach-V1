import os, requests

def check_env_vars(required_vars):
    print("🔍 Checking environment variables...")
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print("❌ Missing:", ", ".join(missing))
    else:
        print("✅ All environment variables set.")

def check_api_health(base_url):
    print("\n🌐 Checking API health...")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        print("Status:", r.status_code, "-", r.text[:120])
    except Exception as e:
        print("❌ Health check failed:", e)

def check_security_headers(base_url):
    print("\n🛡️ Checking security headers...")
    try:
        r = requests.get(base_url, timeout=10)
        headers = ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security"]
        for h in headers:
            print(f"{h}: {'✅' if h in r.headers else '⚠️ missing'}")
    except Exception as e:
        print("❌ Could not verify headers:", e)

if __name__ == "__main__":
    BASE_URL = os.getenv("PRODUCTION_DOMAIN", "https://alistach.vercel.app")
    REQUIRED_VARS = ["INTERNAL_API_KEY", "ADMIN_API_KEY", "JWT_SECRET_KEY"]

    print(f"\n🚀 AliStach-V1 Security & Health Check for {BASE_URL}")
    check_env_vars(REQUIRED_VARS)
    check_api_health(BASE_URL)
    check_security_headers(BASE_URL)
    print("\n✅ Check complete.")
