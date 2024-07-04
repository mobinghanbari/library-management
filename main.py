from fastapi import FastAPI, Depends, Request, HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from database.models import Base, Book
from database.connection import engine, get_db
from fastapi_limiter import FastAPILimiter
from api.users.router import user_app
from api.ips.router import ip_app
from api.categories.router import category_app
from api.authors.router import author_app
from api.books.router import book_app
from api.book_images.router import book_image_app
from api.borrows.router import borrow_app
from api.reports.router import report_app
from api.chang_roles.router import change_role_app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from middlewares.logging_middleware import LoggingMiddleware
from cache.async_connection import redis_client
import os
from dependency.dependency import verify_ip



app = FastAPI(title="Library Management", description="Library Management System (full option)")
templates = Jinja2Templates(directory="templates")
app.include_router(user_app)
app.include_router(ip_app)
app.include_router(category_app)
app.include_router(author_app)
app.include_router(book_app)
app.include_router(book_image_app)
app.include_router(borrow_app)
app.include_router(report_app)
app.include_router(change_role_app)

# Add the logging middleware
app.add_middleware(LoggingMiddleware)


# Mount
this_directory = os.path.dirname(__file__)

app.mount("/static", StaticFiles(directory=os.path.join(this_directory, "static")))

counter = 0
BLACKLIST_THRESHOLD = 3  # Number of attempts before blacklisting
BLACKLIST_DURATION = 24 * 60 * 60  # Blacklist duration in seconds (24 hours)


# Initialize FastAPILimiter with Redis connection
@app.on_event("startup")
async def startup_event():
    global counter
    await FastAPILimiter.init(redis=redis_client)


@app.middleware("http")
async def block_ip_counter(request: Request, call_next):
    global counter
    client_ip = request.client.host
    is_blacklisted = await redis_client.exists(f"blacklist:{client_ip}")

    if is_blacklisted:
        return JSONResponse(status_code=403, content={"message": "Your IP is blacklisted"})

    response = await call_next(request)

    if response.status_code == 429:  # HTTP 429 Too Many Requests
        counter += 1
        print(counter)
        if counter >= BLACKLIST_THRESHOLD:
            await redis_client.setex(f"blacklist:{client_ip}", BLACKLIST_DURATION, "true")
            counter = 0  # Reset counter after blacklisting
            print(f"IP {client_ip} is blacklisted")

    return response


Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def read_latest_books(request: Request, db: Session = Depends(get_db)):
    # books = db.query(Book).order_by(Book.created_at.desc()).limit(5).all()
    books = db.query(Book).order_by(Book.id.desc()).limit(5).all()
    return templates.TemplateResponse("latest_books.html", {"request": request, "books": books})


