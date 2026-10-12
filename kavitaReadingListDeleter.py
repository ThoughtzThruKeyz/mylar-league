import requests
from urllib.parse import urlparse

url = input("Paste in your full OPDS URL from Kavita (Settings > Account > Auth Keys / OPDS): ").strip()
parsed_url = urlparse(url)

# The OPDS URL is https://host[/base-url]/api/opds/<auth key>. Keep the base url, if Kavita has one.
base_path, found, api_key = parsed_url.path.partition("/api/opds/")
api_key = api_key.split('/')[0]
if not parsed_url.netloc or not found or not api_key:
    print("That doesn't look like a Kavita OPDS URL. It should end in /api/opds/ followed by your key.")
    exit()

host_address = parsed_url.scheme + "://" + parsed_url.netloc + base_path.rstrip('/')

print("Host Address:", host_address)

login_endpoint = "/api/Plugin/authenticate"
#search_endpoint = "/api/Search/search?queryString="
deleteRL_endpoint = "/api/ReadingList?readingListId="
listRL_endpoint = "/api/ReadingList/lists"

try:
    apikeylogin = requests.post(host_address + login_endpoint, params={"apiKey": api_key, "pluginName": "CheckSeries"})
    apikeylogin.raise_for_status() # check if the response code indicates an error
    jwt_token = apikeylogin.json()['token']
except requests.exceptions.RequestException as e:
    print("Error during authentication:", e)
    exit()

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}
RLlistURL = host_address + listRL_endpoint

RLIDS = []
try:

    response = requests.post(RLlistURL, headers=headers)
    response.raise_for_status()
    json_data = response.json()
    
    for item in json_data:
        RLID = item['id']
        RLIDS.append(RLID)

except requests.exceptions.RequestException as e:
    print("Error during reading list request:", e)
    exit()

print(f'Found {len(RLIDS)} reading lists in Kavita')

confirmation = input("Do you want to DELETE ALL READING LISTS? (This CANNOT BE UNDONE) Type: Yes to continue: ")
if confirmation == 'Yes':
    try: 
        for listid in RLIDS:
            print(f'Deleting Reading List ID: {listid}')
            RLlistURL = host_address + deleteRL_endpoint + str(listid)
            response_DL = requests.delete(RLlistURL, headers=headers)
            print(response_DL.text)
    except requests.exceptions.RequestException as e:
        print("Error during delete request:", e)
        exit()
else:
    print('Exiting...  No changes made')

print('\n\nTo prevent Reading Lists from being added again:\n     Click on the 3 dots next to your library\n     Settings, then Advanced\n     Untick Manage Reading Lists.')