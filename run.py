import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    flask_debug_env = os.getenv("FLASK_DEBUG")
    if flask_debug_env is not None:
        debug_mode = flask_debug_env.lower() in ("true", "1", "yes")
    else:
        debug_mode = app.config.get("DEBUG", False)

    env_name = app.config.get("ENV_NAME", "development")
    db_name = app.config.get("MONGO_DB_NAME", "unknown")

    print("\n" + "=" * 55, flush=True)
    print("🚀 Book Finder App berjalan!", flush=True)
    print(f"🌍 Mode / Environment : {env_name.upper()} (DEBUG={debug_mode})", flush=True)
    print(f"🗄️ Database           : {db_name}", flush=True)
    print("👉 Buka di browser     : http://localhost:5001", flush=True)
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

