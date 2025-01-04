import requests

cid = 14798  # Example CID for Sodium Hydroxide
url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/safetyandhazards.json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)  # Inspect the data for safety-related information
else:
    print(f"Error fetching data: {response.status_code}")
