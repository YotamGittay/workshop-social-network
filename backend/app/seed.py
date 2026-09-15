from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from .models import Follow, Post, User

USERS = [
    ("alice", "Alice Anderson"),
    ("bob", "Bob Brown"),
    ("carol", "Carol Clark"),
    ("dave", "Dave Davis"),
    ("erin", "Erin Evans"),
]

FOLLOWS = [
    ("alice", "bob"),
    ("alice", "carol"),
    ("bob", "carol"),
    ("bob", "dave"),
    ("carol", "dave"),
    ("dave", "alice"),
    ("erin", "alice"),
    ("erin", "bob"),
]

# (author, text, minutes_ago)
POSTS = [
    ("bob", "Just shipped my first Docker container. It only took 47 tries.", 5),
    ("carol", "Coffee count today: 4. Productivity: undefined.", 12),
    ("bob", "Hot take: tabs vs spaces is a personality test.", 26),
    ("carol", "My rubber duck just solved my bug. Again.", 40),
    ("dave", "Running a social network on my laptop. What could go wrong?", 55),
    ("bob", "MinIO makes S3 local. Living in the future.", 70),
    ("carol", "Deployed on a Friday. Send help.", 95),
    ("dave", "I read the error message. Turns out it was telling the truth.", 130),
    ("bob", "SELECT * FROM posts WHERE author = 'me' -- and that's the feed", 180),
    ("carol", "New profile pic coming soon. The blob storage is ready.", 240),
    ("erin", "Lurking here. Nice network.", 300),
    ("alice", "First post! Hello workshop!", 400),
    ("dave", "postgres:16-alpine is my spirit animal", 500),
    ("bob", "Unfollowing everyone who uses light theme.", 600),
]


def seed(db: Session) -> None:
    """Insert demo users/follows/posts. No-op if users already exist."""
    if db.query(User).count() > 0:
        return

    users = {}
    for username, display_name in USERS:
        user = User(username=username, display_name=display_name)
        db.add(user)
        users[username] = user
    db.flush()

    for follower, followee in FOLLOWS:
        db.add(Follow(follower_id=users[follower].id, followee_id=users[followee].id))

    now = datetime.now(timezone.utc)
    for author, text, minutes_ago in POSTS:
        db.add(
            Post(
                author_id=users[author].id,
                text=text,
                created_at=now - timedelta(minutes=minutes_ago),
            )
        )

    db.commit()
