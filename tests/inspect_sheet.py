import pandas as pd
import requests
import io

def inspect_sheet(url, sheet_name="Верстка"):
    try:
        if "/d/" not in url:
            print("Invalid URL")
            return

        sheet_id = url.split("/d/")[1].split("/")[0]
        # Use vizt url or export url. Export is better for pandas.
        # Note: sheet name must be exact.
        # Try without GID first, or use the edit URL replacement trick
        export_url = url.replace("/edit", "/export").replace("?usp=sharing", "?format=csv")
        if "gid=" not in export_url:
             # If no gid, it usually defaults to the first sheet.
             # But let's try to append format=csv explicitly if not present
             if "?format=csv" not in export_url and "&format=csv" not in export_url:
                 export_url += "?format=csv"
        
        print(f"Downloading...")
        response = requests.get(export_url)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), header=None)
        
        print(f"Shape: {df.shape}")
        print("--- All Columns ---")
        print(df.head(20).to_string())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = "https://docs.google.com/spreadsheets/d/18oK50U01PLDFIUYM2rDGwMOujmDBNdOH_eA1ogzj-ko/edit?usp=sharing"
    inspect_sheet(url)
