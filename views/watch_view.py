import flet as ft
import time
from database.db_manager import DatabaseManager
from components.comment_sheet import CommentSheet

class VideoPlayerCard(ft.Container):
    def __init__(self, video_data, db_manager: DatabaseManager, on_refresh=None):
        self.video_data = video_data
        self.db_manager = db_manager
        self.on_refresh = on_refresh
        
        # Resolve page author
        page_id = video_data.get("pageId")
        pages = db_manager.get_pages()
        self.page_author = next((p for p in pages if p.get("id") == page_id), None)
        self.page_name = self.page_author.get("name", "Page User") if self.page_author else "Page User"
        self.page_avatar = self.page_author.get("avatar_url", "") if self.page_author else ""
        
        # State
        self.is_playing = False
        self.is_liked = False
        
        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            padding=12,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            margin=ft.Margin.only(bottom=8),
        )
        
        # 1. Header (Page Avatar, Name, Follow button, Timestamp)
        self.follow_text = ft.Text("Follow" if not video_data.get("isFollowed") else "Following", color=ft.Colors.BLUE_ACCENT_400, size=12, weight=ft.FontWeight.BOLD)
        self.header = ft.Row([
            ft.CircleAvatar(foreground_image_src=self.page_avatar, radius=18),
            ft.Column([
                ft.Row([
                    ft.Text(self.page_name, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.ON_SURFACE),
                    ft.Text(" • ", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(content=self.follow_text, on_click=self._toggle_follow)
                ], spacing=2),
                ft.Text(f"{video_data.get('create_at', '12h ago')} • {video_data.get('seeCount', 0):,} views", size=11, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=2, expand=True),
            ft.IconButton(icon=ft.Icons.MORE_HORIZ, icon_size=18)
        ], spacing=8)
        
        # 2. Description
        self.description = ft.Text(video_data.get("content", ""), size=13, color=ft.Colors.ON_SURFACE)
        
        # 3. Video Player (Native)
        video_url = video_data.get("video", {}).get("video_url", "http://techslides.com/demos/sample-videos/small.mp4")
        self.video_control = ft.Video(
            expand=True,
            playlist=[ft.VideoMedia(video_url)],
            playlist_mode=ft.PlaylistMode.LOOP,
            fill_color=ft.Colors.BLACK,
            aspect_ratio=16/9,
            autoplay=False,
            show_controls=True,
        )
        
        self.video_player_container = ft.Container(
            content=self.video_control,
            height=220,
            border_radius=4,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=ft.Colors.BLACK,
        )
        
        # 4. Reaction Counters
        self.reactions = video_data.get("reactions", {"like": 0, "love": 0, "haha": 0})
        self.total_reacts = sum(self.reactions.values())
        self.total_comments = len(video_data.get("comments", []))
        
        self.counters = ft.Row([
            ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.THUMB_UP, size=10, color=ft.Colors.WHITE), bgcolor=ft.Colors.BLUE_500, shape=ft.BoxShape.CIRCLE, padding=3),
                ft.Text(str(self.total_reacts), size=11, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=4),
            ft.Text(f"{self.total_comments} comments • 4.2k shares", size=11, color=ft.Colors.ON_SURFACE_VARIANT)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # 5. Buttons Row
        self.like_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.THUMB_UP_OUTLINED, color=ft.Colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Like", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_like
        )
        
        self.comment_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=ft.Colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Comment", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_comment_click
        )
        
        self.content = ft.Column([
            self.header,
            self.description,
            self.video_player_container,
            self.counters,
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            ft.Row([self.like_button, self.comment_button, ft.TextButton(
                content=ft.Row([ft.Icon(ft.Icons.SHARE, color=ft.Colors.ON_SURFACE_VARIANT, size=16), ft.Text("Share", size=12, color=ft.Colors.ON_SURFACE_VARIANT)], spacing=6),
                on_click=self._handle_share
            )], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=8)

    def _toggle_follow(self, e):
        # Toggle state
        self.video_data["isFollowed"] = not self.video_data.get("isFollowed")
        self.follow_text.value = "Following" if self.video_data["isFollowed"] else "Follow"
        self.follow_text.color = ft.Colors.ON_SURFACE_VARIANT if self.video_data["isFollowed"] else ft.Colors.BLUE_ACCENT_400
        self.update()

    def _handle_like(self, e):
        self.is_liked = not self.is_liked
        # Update reacts locally
        if self.is_liked:
            self.total_reacts += 1
            self.like_button.content.controls[0].icon = ft.Icons.THUMB_UP
            self.like_button.content.controls[0].color = ft.Colors.BLUE_ACCENT_400
            self.like_button.content.controls[1].color = ft.Colors.BLUE_ACCENT_400
        else:
            self.total_reacts -= 1
            self.like_button.content.controls[0].icon = ft.Icons.THUMB_UP_OUTLINED
            self.like_button.content.controls[0].color = ft.Colors.ON_SURFACE_VARIANT
            self.like_button.content.controls[1].color = ft.Colors.ON_SURFACE_VARIANT
            
        self.counters.controls[0].controls[1].value = str(self.total_reacts)
        self.update()

    def _handle_comment_click(self, e):
        if self.page:
            self.page.bottom_sheet = CommentSheet(
                post_id=self.video_data.get("id"),
                db_manager=self.db_manager,
                on_comment_added=self._refresh_comments
            )
            self.page.bottom_sheet.open = True
            self.page.update()

    def _refresh_comments(self):
        # Refresh comment count
        video = next((v for v in self.db_manager.get_watch_videos() if v.get("id") == self.video_data.get("id")), None)
        if video:
            self.total_comments = len(video.get("comments", []))
            self.counters.controls[1].value = f"{self.total_comments} comments • 4.2k shares"
            self.update()

    def _handle_share(self, e):
        if self.page:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Video shared successfully!"), bgcolor=ft.Colors.GREEN_800)
            self.page.snack_bar.open = True
            self.page.update()


class WatchView(ft.Container):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        super().__init__(
            expand=True,
            padding=ft.Padding.only(left=8, right=8, top=4, bottom=4),
        )
        
        self.scroll_column = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=10
        )
        
        self.content = self.scroll_column
        self.refresh_watch()

    def refresh_watch(self):
        self.scroll_column.controls.clear()
        
        # Header title
        self.scroll_column.controls.append(
            ft.Row([
                ft.Text("Watch", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.IconButton(ft.Icons.SEARCH, icon_size=18),
                    ft.IconButton(ft.Icons.PERSON, icon_size=18)
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        
        # Tabs bar (Local options like "For You", "Live", "Following", "Saved")
        watch_tabs = ft.Row([
            ft.Container(content=ft.Text("For You", size=12, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, padding=ft.Padding.symmetric(vertical=6, horizontal=12), border_radius=12),
            ft.Container(content=ft.Text("Live", size=12), padding=ft.Padding.symmetric(vertical=6, horizontal=12)),
            ft.Container(content=ft.Text("Following", size=12), padding=ft.Padding.symmetric(vertical=6, horizontal=12)),
            ft.Container(content=ft.Text("Saved", size=12), padding=ft.Padding.symmetric(vertical=6, horizontal=12)),
        ], spacing=4)
        self.scroll_column.controls.append(watch_tabs)
        self.scroll_column.controls.append(ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT))
        
        # Videos List
        videos = self.db_manager.get_watch_videos()
        for v in videos:
            self.scroll_column.controls.append(
                VideoPlayerCard(v, self.db_manager, on_refresh=self.refresh_watch)
            )
            
        if self.page:
            self.update()

def get_watch_view(db_manager: DatabaseManager):
    return WatchView(db_manager)
