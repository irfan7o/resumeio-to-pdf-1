from typing import Annotated
from pathlib import Path as FilePath

from fastapi import APIRouter, Path, Query, Request, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.schemas.resumeio import Extension
from app.services.resumeio import ResumeioDownloader

router = APIRouter()

# Get the base directory (project root)
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.post("/download/{rendering_token}")
def download_resume(
    rendering_token: Annotated[str, Path(min_length=24, max_length=24, pattern="^[a-zA-Z0-9]{24}$")],
    image_size: Annotated[int, Query(gt=0)] = 3000,
    extension: Annotated[Extension, Query()] = Extension.jpeg,
):
    """
    Download a resume from resume.io and return it as a PDF.

    Parameters
    ----------
    rendering_token : str
        Rendering Token of the resume to download.
    image_size : int, optional
        Size of the images to download, by default 3000.
    extension : Extension, optional
        Image extension to download, by default "jpeg".

    Returns
    -------
    fastapi.responses.Response
        A PDF representation of the resume with appropriate headers for inline display.
    """
    resumeio = ResumeioDownloader(rendering_token=rendering_token, image_size=image_size, extension=extension)
    return Response(
        resumeio.generate_pdf(),
        headers={"Content-Disposition": f'inline; filename="{rendering_token}.pdf"'},
    )


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    """
    Render the main index page.

    Parameters
    ----------
    request : fastapi.Request
        The request instance.

    Returns
    -------
    fastapi.templating.Jinja2Templates.TemplateResponse
        Rendered template of the main index page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    """
    Serve the favicon.

    Returns
    -------
    fastapi.responses.FileResponse
        The favicon file.
    """
    return FileResponse(str(TEMPLATES_DIR / "logo.png"), media_type="image/png")


@router.get("/favicon.png", include_in_schema=False)
def favicon_png():
    """
    Serve the favicon PNG.

    Returns
    -------
    fastapi.responses.FileResponse
        The favicon PNG file.
    """
    return FileResponse(str(TEMPLATES_DIR / "logo.png"), media_type="image/png")
