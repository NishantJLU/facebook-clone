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
            bgcolor=ft.colors.SURFACE,
            padding=12,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
            margin=ft.margin.only(bottom=8),
        )
        
        # 1. Header (Page Avatar, Name, Follow button, Timestamp)
        self.follow_text = ft.Text("Follow" if not video_data.get("isFollowed") else "Following", color=ft.colors.BLUE_ACCENT_400, size=12, weight=ft.FontWeight.BOLD)
        self.header = ft.Row([
            ft.CircleAvatar(foreground_image_url=self.page_avatar, radius=18),
            ft.Expanded(
                child=ft.Column([
                    ft.Row([
                        ft.Text(self.page_name, weight=ft.FontWeight.BOLD, size=13, color=ft.colors.ON_SURFACE),
                        ft.Text(" • ", size=12, color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Container(content=self.follow_text, on_click=self._toggle_follow)
                    ], spacing=2),
                    ft.Text(f"{video_data.get('create_at', '12h ago')} • {video_data.get('seeCount', 0):,} views", size=11, color=ft.colors.ON_SURFACE_VARIANT)
                ], spacing=2)
            ),
            ft.IconButton(icon=ft.icons.MORE_HORIZ, icon_size=18)
        ], spacing=8)
        
        # 2. Description
        self.description = ft.Text(video_data.get("content", ""), size=13, color=ft.colors.ON_SURFACE)
        
        # 3. Video Player Container (Mocked)
        self.play_icon = ft.Icon(ft.icons.PLAY_ARROW, color=ft.colors.WHITE, size=48)
        self.progress_bar = ft.ProgressBar(value=0, bgcolor=ft.colors.WHITE24, color=ft.colors.RED_400, visible=False)
        self.video_cover = ft.Image(src=video_data.get("video", {}).get("cover_url"), fit=ft.ImageFit.COVER, expand=True)
        
        self.video_player = ft.Container(
            content=ft.Stack([
                self.video_cover,
                # Black overlay
                ft.Container(bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK), expand=True),
                # Play button overlay
                ft.Container(
                    content=self.play_icon,
                    alignment=ft.alignment.center,
                    on_click=self._toggle_play
                ),
                # Video progress slider (at the bottom)
                ft.Container(
                    content=self.progress_bar,
                    alignment=ft.alignment.bottom_center,
                    bottom=0,
                    left=0,
                    right=0
                )
            ]),
            height=220,
            border_radius=4,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=ft.colors.BLACK,
        )
        
        # 4. Reaction Counters
        self.reactions = video_data.get("reactions", {"like": 0, "love": 0, "haha": 0})
        self.total_reacts = sum(self.reactions.values())
        self.total_comments = len(video_data.get("comments", []))
        
        self.counters = ft.Row([
            ft.Row([
                ft.Container(content=ft.Icon(ft.icons.THUMB_UP, size=10, color=ft.colors.WHITE), bgcolor=ft.colors.BLUE_500, shape=ft.BoxShape.CIRCLE, padding=3),
                ft.Text(str(self.total_reacts), size=11, color=ft.colors.ON_SURFACE_VARIANT)
            ], spacing=4),
            ft.Text(f"{self.total_comments} comments • 4.2k shares", size=11, color=ft.colors.ON_SURFACE_VARIANT)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # 5. Buttons Row
        self.like_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.icons.THUMB_UP_OUTLINED, color=ft.colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Like", size=12, color=ft.colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_like
        )
        
        self.comment_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE, color=ft.colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Comment", size=12, color=ft.colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_comment_click
        )
        
        self.content = ft.Column([
            self.header,
            self.description,
            self.video_player,
            self.counters,
            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
            ft.Row([self.like_button, self.comment_button, ft.TextButton(
                content=ft.Row([ft.Icon(ft.icons.SHARE, color=ft.colors.ON_SURFACE_VARIANT, size=16), ft.Text("Share", size=12, color=ft.colors.ON_SURFACE_VARIANT)], spacing=6),
                on_click=self._handle_share
            )], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=8)

    def _toggle_follow(self, e):
        # Toggle state
        self.video_data["isFollowed"] = not self.video_data.get("isFollowed")
        self.follow_text.value = "Following" if self.video_data["isFollowed"] else "Follow"
        self.follow_text.color = ft.colors.ON_SURFACE_VARIANT if self.video_data["isFollowed"] else ft.colors.BLUE_ACCENT_400
        self.update()

    def _toggle_play(self, e):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_icon.name = ft.icons.PAUSE_CIRCLE_FILLED
            self.progress_bar.visible = True
            self.progress_bar.value = 0.1
            self.update()
            
            # Simple simulation: let progress increase a bit
            def simulate_play():
                for i in range(2, 11):
                    if not self.is_playing:
                        break
                    time.sleep(0.4)
                    self.progress_bar.value = i / 10.0
                    try:
                        self.update()
                    except:
                        break
            # Start simulated thread
            import threading
            threading.Thread(target=simulate_play, daemon=True).start()
        else:
            self.play_icon.name = ft.icons.PLAY_ARROW
            self.progress_bar.visible = False
            self.update()

    def _handle_like(self, e):
        self.is_liked = not self.is_liked
        # Update reacts locally
        if self.is_liked:
            self.total_reacts += 1
            self.like_button.content.controls[0].name = ft.icons.THUMB_UP
            self.like_button.content.controls[0].color = ft.colors.BLUE_ACCENT_400
            self.like_button.content.controls[1].color = ft.colors.BLUE_ACCENT_400
        else:
            self.total_reacts -= 1
            self.like_button.content.controls[0].name = ft.icons.THUMB_UP_OUTLINED
            self.like_button.content.controls[0].color = ft.colors.ON_SURFACE_VARIANT
            self.like_button.content.controls[1].color = ft.colors.ON_SURFACE_VARIANT
            
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
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Video shared successfully!"), bgcolor=ft.colors.GREEN_800)
            self.page.snack_bar.open = True
            self.page.update()


class WatchView(ft.Container):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
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
                    ft.IconButton(ft.icons.SEARCH, icon_size=18),
                    ft.IconButton(ft.icons.PERSON, icon_size=18)
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        
        # Tabs bar (Local options like "For You", "Live", "Following", "Saved")
        watch_tabs = ft.Row([
            ft.Container(content=ft.Text("For You", size=12, weight=ft.FontWeight.BOLD), bgcolor=ft.colors.SURFACE_VARIANT, padding=ft.padding.symmetric(6, 12), border_radius=12),
            ft.Container(content=ft.Text("Live", size=12), padding=ft.padding.symmetric(6, 12)),
            ft.Container(content=ft.Text("Following", size=12), padding=ft.padding.symmetric(6, 12)),
            ft.Container(content=ft.Text("Saved", size=12), padding=ft.padding.symmetric(6, 12)),
        ], spacing=4)
        self.scroll_column.controls.append(watch_tabs)
        self.scroll_column.controls.append(ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT))
        
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
