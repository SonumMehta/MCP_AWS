from fastmcp import FastMCP
import requests
from typing import Optional, Dict
import boto3
import json
from config import *

def get_secrets(secret_name: str) -> str:
    """
    Retrieve API key from AWS Secret Manager

    Args:
        secret_name (str): Name of the secret in Secret Manager

    Returns:
        str: API key value
    """
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secrets("MCP_Secrets")

mcp = FastMCP()

def make_api_request(url: str, params: dict, timeout: int = 10) -> Optional[Dict]:
    """
    Make an HTTP GET request to the specified URL with given parameters.
    
    Args:
        url (str): The URL to make the request to
        params (dict): Dictionary of parameters to include in the request
        timeout (int, optional): Request timeout in seconds. Defaults to 10.
    
    Returns:
        Optional[Dict]: JSON response as a dictionary if successful, None if failed
    
    Raises:
        Prints error message to console if request fails
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)
        #Checking if the response status code indicates success
        response.raise_for_status()
        #Trying to parse JSON response
        return response.json()
        
    except requests.exceptions.Timeout:
        print(f"Request timeout after {timeout} seconds for URL: {url}")
        return None
    
    except requests.exceptions.ConnectionError:
        print(f"Connection error occurred for URL: {url}")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error {response.status_code} for URL: {url} - {e}")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request error for URL: {url} - {e}")
        return None
    
    except ValueError as e:
        print(f"JSON decode error for URL: {url} - Invalid JSON response: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error for URL: {url} - {e}")
        return None

@mcp.tool()
def get_policy_details(url: str, params: dict, timeout: int=10 ):
    base_url = GET_POLICY_DETAILS_URL
    params = {
        "api_key": secrets["AA_INTERNAL_API_KEY"]
    }
    result = make_api_request(base_url, params, timeout)
    if result:
        return result
    else:
        return {"error": "Failed to fetch policy details"}


if __name__ == "__main__":
    mcp.run()
