import os
import requests


def login(request):
    # Get the authorization header from the request
    auth_header = request.authorization

    # If the authorization header is not present, return an error
    if not auth_header:
        return None, ("Error: No authentication header provided", 401)

    # Extract the username and password from the authorization header
    username = auth_header.username
    password = auth_header.password

    # Send a POST request to the login endpoint of the auth service
    # with the basic authentication credentials
    response = requests.post(
        f"http://{os.environ['AUTH_SVC_ADDRESS']}/login", auth=(username, password)
    )

    # If the login was successful, return the response text
    if response.status_code == 200:
        return response.text, None
    # Otherwise, return the error message and status code
    else:
        return None, (response.text, response.status_code)
