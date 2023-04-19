from ast import Constant
#do "pip install requests"
import requests
import random
import os
import base64
import json
#do "pip install PyGithub"
from github import Github

# Set the path of the folder to upload to the repository
FOLDER_PATH = "habanero"
filename_original = ".github/workflows/workflow_orig.yml"
filename_original_az = ".github/workflows/workflow_orig_az.yml"

ACCOUNTS = os.environ['GH_ACCOUNTS_B64']
ACCOUNTS = base64.b64decode(ACCOUNTS).decode("utf-8")
data = json.loads(ACCOUNTS)
GOOGLE_SHEETS_TAB_NAME          = os.environ['GOOGLE_SHEETS_TAB_NAME']
GOOGLE_SHEETS_TOKEN_B64         = os.environ['GOOGLE_SHEETS_TOKEN_B64']
GOOGLE_SHEETS_SHEET_ID          = os.environ['GOOGLE_SHEETS_SHEET_ID']
GOOGLE_SHEETS_CREDENTIALS_B64   = os.environ['GOOGLE_SHEETS_CREDENTIALS_B64']
TELEGRAM_API_TOKEN              = os.environ['TELEGRAM_API_TOKEN']
TELEGRAM_USERID                 = os.environ['TELEGRAM_USERID']
GPG_PASSPHRASE                  = os.environ['GPG_PASSPHRASE']
CONTAINER_IMAGE                 = os.environ['CONTAINER_IMAGE']
CONTAINER_USER                  = os.environ['CONTAINER_USER']
CONTAINER_PASS                  = os.environ['CONTAINER_PASS']
MATRIX                          = os.environ['MATRIX']
AZURE_CREDENTIALS               = os.environ['AZURE_CREDENTIALS']

message = "Jobs will start tomorrow at:\n"
# set in CET
startHours = 10
endHours = 12

for item in data:
    print("ID: "        , item["id"])
    print("Account: "   , item["account"])
    #print("Token: "    , item["token"])
    try:
        # Instantiate the Github object using the access token
        g = Github(item["token"])

        # Ottiene l'istanza dell'utente
        user = g.get_user(item["account"])
        # Itera sulle repository dell'utente e stampa il nome della prima
        for repo in user.get_repos():
            #print(repo.name)
            wf = repo.get_workflow(f"{repo.name}.yml")
            runs = wf.get_runs()
            run_count = 0
            for run in runs:
                run_count += 1
            
            if run_count == 0:
                print('Number of runs:', run_count)
                print(f"Workflow: {wf.name}")
            
                response = requests.get("https://api.datamuse.com/words", params={"rel_jjb": "cool"})
                first_word = random.choice(response.json())["word"]
                response = requests.get("https://api.datamuse.com/words", params={"rel_jjb": "project"})
                second_word = random.choice(response.json())["word"]
                REPO_NAME = f"{first_word}-{second_word}"
                print(REPO_NAME)
                hour = random.randint(startHours, endHours)
                minute = random.randint(0, 59)
                #set in UTC
                cron = f"{minute} {hour-2} * * *"
                #message = message + f"{hour}:{minute} for {item['id']} - {item['account']}\n"
                message = message + f"{str(hour).zfill(2)}:{str(minute).zfill(2)} for {str(item['id']).zfill(3)} - {item['account']}\n"
                repo = g.get_user().create_repo(REPO_NAME)
                print(f"Repository {REPO_NAME} creata correttamente")
                print('Add files to repository')
                filename_output = f".github/workflows/{REPO_NAME}.yml" 
                with open(os.path.join(FOLDER_PATH, filename_original), 'r') as file :
                    filedata = file.read()
                filedata = filedata.replace('__name__'      , REPO_NAME)
                filedata = filedata.replace('__cron__'      , cron)
                filedata = filedata.replace('__affinity__'  , item["id"])
                filedata = filedata.replace('__account__'   , item["account"])
                with open(os.path.join(FOLDER_PATH, filename_output), 'w') as file:
                    file.write(filedata)
                print('Add files to repository az')
                #set in UTC
                cron = f"{minute} {hour+4} * * *"
                filename_output_az = f".github/workflows/{REPO_NAME}_az.yml" 
                with open(os.path.join(FOLDER_PATH, filename_original_az), 'r') as file :
                    filedata = file.read()
                filedata = filedata.replace('__name__'      , REPO_NAME)
                filedata = filedata.replace('__cron__'      , cron)
                filedata = filedata.replace('__affinity__'  , item["id"])
                filedata = filedata.replace('__account__'   , item["account"])
                with open(os.path.join(FOLDER_PATH, filename_output_az), 'w') as file:
                    file.write(filedata)
                # Add the files from the folder to the repository
                exclude_list = ["workflow_orig.yml", ".DS_Store", "workflow_orig_az.yml"]
                for dirname, _, filenames in os.walk(FOLDER_PATH):
                    for filename in filenames:
                        if filename in exclude_list:
                            continue
                        file_path = os.path.join(dirname, filename)
                        with open(file_path, "rb") as f:
                            contents = f.read()
                        file_path_relative = os.path.relpath(file_path, FOLDER_PATH)
                        print(file_path_relative)
                        repo.create_file(file_path_relative, f"Added {file_path_relative}", contents)
                os.remove(f"{FOLDER_PATH}/{filename_output}")
                os.remove(f"{FOLDER_PATH}/{filename_output_az}")
                print('Add files to repository completed')
                print('Creation secret')
                # Create the secret using the create_secret() method
                repo.create_secret("GOOGLE_SHEETS_TAB_NAME"         , GOOGLE_SHEETS_TAB_NAME)
                repo.create_secret("GOOGLE_SHEETS_TOKEN_B64"        , GOOGLE_SHEETS_TOKEN_B64)
                repo.create_secret("GOOGLE_SHEETS_SHEET_ID"         , GOOGLE_SHEETS_SHEET_ID)
                repo.create_secret("GOOGLE_SHEETS_CREDENTIALS_B64"  , GOOGLE_SHEETS_CREDENTIALS_B64)
                repo.create_secret("TELEGRAM_API_TOKEN"             , TELEGRAM_API_TOKEN)
                repo.create_secret("TELEGRAM_USERID"                , TELEGRAM_USERID)
                repo.create_secret("GPG_PASSPHRASE"                 , GPG_PASSPHRASE)
                repo.create_secret("CONTAINER_IMAGE"                , CONTAINER_IMAGE)
                repo.create_secret("CONTAINER_USER"                 , CONTAINER_USER)
                repo.create_secret("CONTAINER_PASS"                 , CONTAINER_PASS)
                repo.create_secret("MATRIX"                         , MATRIX)
                #repo.create_secret("AZURE_CREDENTIALS"              , AZURE_CREDENTIALS)
                print(f"Secret set correctly in the repository {REPO_NAME}.")
                print("----------------------------------------------------")
                # Impostare l'URL per inviare l'evento di dispatch
                url = f"https://api.github.com/repos/{item['account']}/{repo.name}/actions/workflows/{repo.name}.yml/dispatches"
                # Impostare l'header per l'autenticazione e la versione dell'API
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {item['token']}",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                # Impostare il corpo della richiesta con il nome del branch target per il workflow
                payload = {
                    "ref": "main"
                }
                # Effettuare la richiesta HTTP POST per inviare l'evento di dispatch
                response = requests.post(url, headers=headers, json=payload)
                print(response.text)
                # Stampare la risposta HTTP
                print(response.status_code)
            break
    except Exception as e:
        # If an error occurs, add the error message to the message string
        message = message + f"{str(item['id']).zfill(3)} - {item['account']} - Error: {str(e)}\n"
        print(message)
        continue

# Send notification to telegram
print("Send notification to telegram")
url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage?chat_id={TELEGRAM_USERID}&text={message}"
print(message)
print(requests.get(url).json()) # this sends the message