import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Form, FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import markdown2

app = FastAPI()
templates = Jinja2Templates(directory="templates")
saves_dir = "saves"


@app.get("/")
def preview_markdown(request: Request):
    with open("content.md", "r") as file:
        markdown_content = file.read()

    html_content = markdown2.markdown(markdown_content)
    return templates.TemplateResponse("index.html", {"request": request, "content": html_content})


def get_saved_files():
    saved_files = [filename for filename in os.listdir(
        saves_dir) if not filename.startswith(".")]
    saved_files.sort()
    return saved_files


@app.get("/filenames")
async def get_filenames():
    return {"filenames": get_saved_files()}


@app.get("/view/{filename}", response_class=JSONResponse)
async def view_file(filename: str, request: Request):
    try:
        with open(os.path.join(saves_dir, filename), 'r') as file:
            content = file.read()
        data = {"filename": filename, "content": content}
        return data
    except FileNotFoundError:
        return Response(content="File not found", status_code=404)


@app.post("/saves", status_code=201)
@app.post("/saves/{filename}", status_code=200)
async def save_content(content: Annotated[str, Form()], response: Response, filename: str = ''):
    if filename == "":
        timestamp = datetime.now(
            timezone(timedelta(hours=+8))).strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}.txt"

    if not os.path.exists(saves_dir):
        os.mkdir(saves_dir)

    filepath = os.path.join(saves_dir, filename)
    if not os.path.exists(filepath):
        response.status_code = status.HTTP_201_CREATED
    with open(filepath, 'w') as file:
        file.write(content)
    return {"message": f"Saved as {filename}!", "filename": filename}


@app.get("/saves", response_class=HTMLResponse)
def get_saves(request: Request):
    saved_files = get_saved_files()
    return templates.TemplateResponse("save.html", {"request": request, "saved_files": saved_files})


@app.delete("/saves/{filename}")
async def delete_file(filename: str):
    try:
        os.remove(os.path.join(saves_dir, filename))
        return {"message": f"{filename} deleted successfully!"}
    except FileNotFoundError:
        return {"message": f"File {filename} not found.", "status_code": 404}
