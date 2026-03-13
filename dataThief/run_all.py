import subprocess
import concurrent.futures
import time
import sys

# List the file names of the scripts you want to run
SCRIPTS = [
    "dataThief/dataScrapperAPI/auchan_api_scraper.py",
    "dataThief/dataScrapperAPI/continente_api_scraper.py",
    "dataThief/dataScrapperAPI/intermarche_api_scraper.py",
    "dataThief/dataScrapperAPI/lidl_api_scraper.py",
    "dataThief/dataScrapperAPI/minipreco_api_scraper.py",
    "dataThief/dataScrapperAPI/pingodoce_api_scraper.py",
]

def run_script(script_name):
    """Function to run a single python script and capture its output."""
    print(f"🚀 Starting: {script_name}")
    start_time = time.time()
    
    try:
        # Runs the script and waits for it to finish
        # We use sys.executable to ensure we use the same python version
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False, # Set to True if you want to hide their logs
            text=True
        )
        
        duration = time.time() - start_time
        if result.returncode == 0:
            print(f"✅ Finished: {script_name} in {duration:.2f}s")
        else:
            print(f"❌ Failed: {script_name} (Exit Code: {result.returncode})")
            
    except Exception as e:
        print(f"🚨 Error running {script_name}: {e}")

def main():
    print("--- 🛒 Multi-Store Scraper Orchestrator ---")
    total_start = time.time()

    # Use ProcessPoolExecutor to run scripts in parallel
    # max_workers determines how many scripts run at once
    with concurrent.futures.ProcessPoolExecutor(max_workers=len(SCRIPTS)) as executor:
        executor.map(run_script, SCRIPTS)

    total_duration = time.time() - total_start
    print(f"\n✨ All tasks complete! Total execution time: {total_duration:.2f}s")

if __name__ == "__main__":
    main()