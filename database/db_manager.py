import json
import os
import threading

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path=None):
        if self._initialized:
            return
        # Prioritize env variable, then parameter, then default
        self.db_path = os.getenv("DB_PATH", db_path or "database/db.json")
        self.data = {}
        self.active_user_id = 1  # Default to "NishantJLU"
        self.load_db()
        self._initialized = True

    def load_db(self):
        with self._lock:
            if os.path.exists(self.db_path):
                try:
                    with open(self.db_path, "r", encoding="utf-8") as f:
                        self.data = json.load(f)
                    if not self.data:
                        self._initialize_default_db()
                except Exception as e:
                    print(f"Error loading database: {e}")
                    self._initialize_default_db()
            else:
                self._initialize_default_db()

    def _initialize_default_db(self):
        """Initialize a minimal valid database structure if missing or empty."""
        self.data = {
            "users": [
                {"id": 1, "name": "NishantJLU", "avatar_url": "https://i.pravatar.cc/150?u=1"}
            ],
            "posts": [],
            "stories": [],
            "recommend_friends": [],
            "friend_requests": [],
            "groups": [],
            "group_posts": [],
            "group_categories": [],
            "watch_videos": [],
            "notifications": [],
            "products": [],
            "pages": []
        }
        self.save_db()

    def save_db(self):
        with self._lock:
            try:
                # Ensure the folder exists
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                with open(self.db_path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving database: {e}")

    # --- User Helpers ---
    def get_users(self):
        return self.data.get("users", [])

    def get_user(self, user_id):
        for u in self.get_users():
            if u.get("id") == user_id:
                return u
        return None

    def get_active_user(self):
        return self.get_user(self.active_user_id)

    def set_active_user(self, user_id):
        self.active_user_id = user_id
        return self.get_active_user()

    # --- Post Helpers ---
    def get_posts(self):
        return self.data.get("posts", [])

    def get_post(self, post_id):
        for p in self.get_posts():
            if p.get("id") == post_id:
                return p
        return None

    def add_post(self, content, image_url=None):
        posts = self.get_posts()
        new_id = max([p.get("id", 0) for p in posts]) + 1 if posts else 1
        new_post = {
            "id": new_id,
            "image": image_url or "",
            "create_at": "Just now",
            "content": content,
            "userId": self.active_user_id,
            "reactions": {"like": 0, "love": 0, "haha": 0, "wow": 0, "sad": 0, "angry": 0},
            "permission": 1,
            "comments": []
        }
        posts.insert(0, new_post)  # Add to top of feed
        self.data["posts"] = posts
        self.save_db()
        return new_post

    def like_post(self, post_id, reaction_type="like", increment=True):
        post = self.get_post(post_id)
        if post:
            reactions = post.setdefault("reactions", {"like": 0, "love": 0, "haha": 0, "wow": 0, "sad": 0, "angry": 0})
            current_val = reactions.get(reaction_type, 0)
            if increment:
                reactions[reaction_type] = current_val + 1
            else:
                reactions[reaction_type] = max(0, current_val - 1)
            self.save_db()
            return post
        return None

    def add_comment(self, post_id, content, image_url=None):
        post = self.get_post(post_id)
        if post:
            active_user = self.get_active_user()
            comments = post.setdefault("comments", [])
            new_id = max([c.get("id", 0) for c in comments]) + 1 if comments else 1
            new_comment = {
                "id": new_id,
                "name": active_user.get("name", "Anonymous"),
                "avatar_url": active_user.get("avatar_url", ""),
                "image": image_url or "",
                "content": content,
                "create_at": "Just now"
            }
            comments.append(new_comment)
            self.save_db()
            return new_comment
        return None

    # --- Stories Helpers ---
    def get_stories(self):
        return self.data.get("stories", [])

    # --- Friends Helpers ---
    def get_recommended_friends(self):
        return self.data.get("recommend_friends", [])

    def get_friend_requests(self):
        return self.data.get("friend_requests", [])

    def accept_friend_request(self, request_id):
        requests = self.get_friend_requests()
        for r in requests:
            if r.get("id") == request_id:
                # Remove from request list
                requests.remove(r)
                self.data["friend_requests"] = requests
                # Add to friends list (for testing simplification)
                active_user = self.get_active_user()
                if active_user:
                    friends = active_user.setdefault("friends", [])
                    friends.append({"userId": r.get("userId"), "mutualFriends": 0})
                self.save_db()
                return True
        return False

    # --- Groups Helpers ---
    def get_groups(self):
        return self.data.get("groups", [])

    def get_group_posts(self):
        return self.data.get("group_posts", [])

    def get_group_categories(self):
        return self.data.get("group_categories", [])

    # --- Watch Videos Helpers ---
    def get_watch_videos(self):
        return self.data.get("watch_videos", [])

    # --- Notifications Helpers ---
    def get_notifications(self):
        return self.data.get("notifications", [])

    # --- Marketplace Products Helpers ---
    def get_products(self):
        return self.data.get("products", [])

    # --- Pages Helpers ---
    def get_pages(self):
        return self.data.get("pages", [])
