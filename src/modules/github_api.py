import jwt
import requests
import time
from datetime import datetime, timezone, timedelta
from requests.exceptions import RequestException, ConnectionError

import settings as st


def generate_jwt(config):
    with open(config["PRIVATE_KEY_PATH"], "r") as f:
        private_key = f.read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": config["APP_ID"]
    }

    return jwt.encode(payload, private_key, algorithm="RS256")

def get_access_token():
    if st.TOKEN_MODE == "GITHUB_APP_TOKEN":
        jwt_token = generate_jwt(st.GITHUB_APP_CONFIG)
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.post(
            f'https://api.github.com/app/installations/{st.GITHUB_APP_CONFIG["INSTALLATION_ID"]}/access_tokens', 
            headers=headers
            )
        data = response.json()
        return data["token"], data["expires_at"]
    
    elif st.TOKEN_MODE == "PERSONAL_ACCESS_TOKEN":
        return st.PERSONAL_ACCESS_TOKEN, None
    

def get_rate_limit(response):
    limit_num = response.headers.get("X-RateLimit-Limit")
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset_time = response.headers.get("X-RateLimit-Reset")

    reset_time_utc = datetime.fromtimestamp(int(reset_time),tz=timezone.utc)

    return limit_num, remaining, reset_time_utc


def request_github_api(api_url, access_token):
    headers = {
        "Authorization": f"token {access_token}",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    retries = 0
    while retries <= st.API_MAX_RETRIES:
        try:
            response = requests.get(
                url = api_url,
                headers = headers
            )

            if response.status_code == 200:
                return True, response
            else:
                # print(f"Error: {api_url} Status Code: {response.status_code}")
                return False, {"error": "API Error", "status_code": response.status_code, "response": response.text}

        except (RequestException, ConnectionError) as e:
            # print(f'\nSleep : {api_url} for NetWork Error')
            time.sleep(st.API_RETRY_DELAY)
            retries += 1
            if retries > st.API_MAX_RETRIES:
                print(f'\nNetwork Error: {api_url} {e}')
                return False, {"error": "Network Error"}
        
        except Exception as e:
            # print(f'\nSleep : {api_url} for Other Error')
            time.sleep(st.API_RETRY_DELAY)
            retries += 1

            if retries > st.API_MAX_RETRIES:
                print(f"\nError: {api_url} {e}")
                return False, {"error": str(e)}


# [ToDo] This part is under development
# def check_access_token(access_token):
#     url = "https://api.github.com/rate_limit"
#     headers = {
#         "Authorization": f"token {access_token}",
#         "Accept": "application/vnd.github.v3+json" 
#     }

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         print(response.json())
#         return True, response.json()
#     except RequestException as e:
#         print(f"[Error] Access token check failed. Please verify the token in settings.py.")
#         return False, None


def call_workflows_api(repository_name, access_token):
    api_url = f'https://api.github.com/repos/{repository_name}/actions/workflows'
    return request_github_api(api_url, access_token)


def call_get_repository_tags_api(repository_name, access_token, page_id = 1):
    api_url = f'https://api.github.com/repos/{repository_name}/tags?per_page=100&page={page_id}'
    return request_github_api(api_url, access_token)


def call_get_repository_branches_api(repository_name, access_token, page_id = 1):
    api_url = f'https://api.github.com/repos/{repository_name}/branches?per_page=100&page={page_id}'
    return request_github_api(api_url, access_token)


def call_get_repository_api(repository_name, access_token):
    api_url = f'https://api.github.com/repos/{repository_name}'
    return request_github_api(api_url, access_token)