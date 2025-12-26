import sys
import os
import dash

# Fix Path
sys.path.append(os.getcwd())

def verify_app():
    print("--- Verifying Dashboard App Startup ---")
    try:
        from src.dashboard.app import app
        print("[SUCCESS] App imported successfully.")
        
        # Check Layout
        if app.layout:
            print("[SUCCESS] Layout initialized.")
        else:
            print("[FAILED] Layout is None.")
            sys.exit(1)
            
        # Check Callbacks
        if app.callback_map:
            print(f"[SUCCESS] {len(app.callback_map)} callbacks registered.")
        else:
             print("[WARNING] No callbacks registered.")

        print("\nAll checks passed.")
        
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] App crashed on startup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_app()
