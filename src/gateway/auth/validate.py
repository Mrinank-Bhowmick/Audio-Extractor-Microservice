import os
import requests

def validate_token(request):
    """
    Validate the provided token by sending a request to the auth service.
    Returns the token and a tuple containing an error message and status code
    if the validation fails.
    """
    # Check if the request contains an "Authorization" header
    if "Authorization" not in request.headers:
        return None, ("Error: No authentication header provided", 401)
    
    # Get the token from the "Authorization" header
    token = request.headers["Authorization"]
    
    # If the token is not present, return an error
    if not token:
        return None, ("Error: No token provided", 401)
    
    # Send a POST request to the validate endpoint of the auth service
    # with the token in the "Authorization" header
    response = requests.post(
        f"http://{os.environ['AUTH_SVC_ADDRESS']}/validate",
        headers={"Authorization": token}
    )
    
    # If the token was successfully validated, return the response text
    if response.status_code == 200:
        return response.text, None
    # Otherwise, return the error message and status code
    else:
        return None, (response.text, response.status_code)
 