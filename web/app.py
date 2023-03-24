from fastapi import FastAPI, Form, Request, File, Response, UploadFile, Cookie, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import os
import aiohttp

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader(os.path.abspath("./templates")))


@app.get("/", response_class=HTMLResponse)
async def home():
    return "Register route - /register , Login route - /login , Upload route - /upload , Download route - /download , Logout route - /logout"


@app.get("/login", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login_done", response_class=HTMLResponse)
async def process_login(
    response: Response, username: str = Form(...), password: str = Form(...)
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://mp3convertor.mrinank-bhowmick.cloud.okteto.net/login",
            auth=aiohttp.BasicAuth(username, password),
        ) as token:
            JWT_token = await token.text()
            if token.status == 401:
                return "Invalid credentials"
            if token.status == 200:
                response = RedirectResponse(url="/upload", status_code=303)
                response.set_cookie(
                    key="token", value=JWT_token, secure=True, max_age=3600
                )
                return response


@app.get("/register", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register_done", response_class=HTMLResponse)
async def process_register(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    return templates.TemplateResponse(
        "result.html", {"request": request, "username": username, "password": password}
    )


@app.get("/upload", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


# This will post the mp4 file to the server
@app.post("/uploading", response_class=HTMLResponse)
async def process_upload(request: Request, file: UploadFile = File(...)):
    token = request.cookies.get("token")

    contents = await file.read()

    # Upload the file to the server with the Bearer token in the header of the request
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        data = aiohttp.FormData()
        data.add_field(
            "file", contents, filename=file.filename, content_type="video/mp4"
        )
        async with session.post(
            "http://mp3convertor.mrinank-bhowmick.cloud.okteto.net/upload",
            headers=headers,
            data=data,
        ) as response:
            # capture the message from the server
            message = await response.text()
            print(message)
            if response.status == 200:
                # add template response in redirect response
                response = RedirectResponse(url="/upload", status_code=303)
                response.set_cookie(key="token", value=token, secure=True, max_age=3600)

                content = env.get_template("upload.html").render(show_download=True)
                response = HTMLResponse(content=content)
                return response

            else:
                response = RedirectResponse(url="/upload", status_code=303)
                content = env.get_template("upload.html").render(show_download="Failed")
                response = HTMLResponse(content=content)
                return response


@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/testing", response_class=HTMLResponse)
async def process_upload(response: Response):
    show_download = True
    response = RedirectResponse(url="/test", status_code=303)
    content = env.get_template("upload.html").render(
        message="Conversion successful!", show_download=show_download
    )
    response = HTMLResponse(content=content)

    return response


@app.get("/logout", response_class=HTMLResponse)
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="token", domain=".vercel.com")
    return response
