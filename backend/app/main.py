import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Follow, Post, User
from .schemas import PostOut, UserOut
from .seed import seed
from .storage import ALLOWED_TYPES, MAX_UPLOAD_BYTES, ensure_bucket, upload_image


def init_db() -> None:
    """Create tables and seed. Retry while Postgres is still waking up."""
    for attempt in range(30):
        try:
            Base.metadata.create_all(engine)
            db = next(get_db())
            try:
                seed(db)
            finally:
                db.close()
            return
        except OperationalError:
            if attempt == 29:
                raise
            time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ensure_bucket()
    yield


app = FastAPI(title="Workshop Social Network", lifespan=lifespan)

# Not strictly needed (nginx proxies everything on one origin),
# but handy when hitting the backend directly on :8000 during dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def current_user(
    x_user_id: int | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    user = db.get(User, x_user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="unknown user")
    return user


def to_post_out(post: Post) -> PostOut:
    return PostOut(
        id=post.id,
        text=post.text,
        image_url=f"/images/{post.image_key}" if post.image_key else None,
        created_at=post.created_at,
        author=UserOut.model_validate(post.author),
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@app.get("/api/users/me/following", response_model=list[UserOut])
def list_following(me: User = Depends(current_user), db: Session = Depends(get_db)):
    return (
        db.query(User)
        .join(Follow, Follow.followee_id == User.id)
        .filter(Follow.follower_id == me.id)
        .order_by(User.id)
        .all()
    )


@app.post("/api/follows/{user_id}", status_code=204)
def follow(user_id: int, me: User = Depends(current_user), db: Session = Depends(get_db)):
    if user_id == me.id:
        raise HTTPException(status_code=400, detail="cannot follow yourself")
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="user not found")
    if db.get(Follow, (me.id, user_id)) is None:
        db.add(Follow(follower_id=me.id, followee_id=user_id))
        db.commit()


@app.delete("/api/follows/{user_id}", status_code=204)
def unfollow(user_id: int, me: User = Depends(current_user), db: Session = Depends(get_db)):
    follow_row = db.get(Follow, (me.id, user_id))
    if follow_row is not None:
        db.delete(follow_row)
        db.commit()


@app.get("/api/feed", response_model=list[PostOut])
def get_feed(me: User = Depends(current_user), db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .join(Follow, Follow.followee_id == Post.author_id)
        .filter(Follow.follower_id == me.id)
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )
    return [to_post_out(p) for p in posts]


@app.post("/api/posts", response_model=PostOut, status_code=201)
async def create_post(
    text: str = Form(...),
    image: UploadFile | None = File(default=None),
    me: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    image_key = None
    if image is not None and image.filename:
        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"unsupported image type: {image.content_type}",
            )
        data = await image.read()
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=400, detail="image too large (max 5 MB)")
        image_key = upload_image(data, image.content_type)

    post = Post(author_id=me.id, text=text, image_key=image_key)
    db.add(post)
    db.commit()
    db.refresh(post)
    return to_post_out(post)
