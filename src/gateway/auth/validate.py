import os
import requests

def token(request):
    if not "Authorization" in request.headers:
        return None, ("No authentication header provided", 401)
    
    token = request.headers["Authorization"]
    
    if not token:
        return None, ("No token provided", 401)
    
    response = requests.post(
        f"http://{os.environ['AUTH_SVC_ADDRESS']}/validate",
        headers={"Authorization": token}
    )
    
    if response.status_code == 200:
        return response.txt, None
    else:
        return None, (response.txt, response.status_code)