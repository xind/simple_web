from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import markdown2

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def preview_markdown(request: Request):
    with open("content.md", "r") as file:
        markdown_content = file.read()

    html_content = markdown2.markdown(markdown_content)
    return templates.TemplateResponse("index.html", {"request": request, "content": html_content})
