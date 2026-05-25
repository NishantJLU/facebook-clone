import flet as ft
from database.db_manager import DatabaseManager
from components.composer import Composer
from components.story_card import get_stories_row
from components.post_card import PostCard

class HomeView(ft.Container):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
        )
        
        # Scrollable Feed Column
        self.feed_column = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=8
        )
        
        self.content = self.feed_column
        self.refresh_feed()

    def refresh_feed(self, e=None):
        self.feed_column.controls.clear()
        
        # 1. Composer
        composer = Composer(self.db_manager, on_write_post=self._open_create_post_dialog)
        self.feed_column.controls.append(composer)
        
        # 2. Stories Section
        stories_row = get_stories_row(
            self.db_manager, 
            on_story_click=self._handle_story_click,
            on_create_story=self._handle_create_story
        )
        stories_container = ft.Container(
            content=stories_row,
            bgcolor=ft.colors.SURFACE,
            padding=10,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK))
        )
        self.feed_column.controls.append(stories_container)
        
        # 3. Posts List
        posts = self.db_manager.get_posts()
        for post in posts:
            post_card = PostCard(post, self.db_manager, on_post_updated=self.refresh_feed)
            self.feed_column.controls.append(post_card)
        
        if self.page:
            self.update()

    def _open_create_post_dialog(self, e):
        if not self.page:
            return
            
        active_user = self.db_manager.get_active_user()
        post_input = ft.TextField(
            hint_text=f"What's on your mind, {active_user.get('name', 'User')}?",
            multiline=True,
            min_lines=3,
            max_lines=6,
            border_color=ft.colors.TRANSPARENT,
            bgcolor=ft.colors.TRANSPARENT,
            content_padding=0,
            autofocus=True
        )
        
        image_input = ft.TextField(
            hint_text="Paste an Image URL (optional)...",
            border_radius=8,
            text_size=12,
            content_padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_color=ft.colors.TRANSPARENT
        )
        
        def submit_post(_):
            content_text = post_input.value.strip()
            img_url = image_input.value.strip()
            
            if not content_text and not img_url:
                return
                
            self.db_manager.add_post(content_text, img_url)
            self.page.dialog.open = False
            self.refresh_feed()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Post published successfully!"),
                bgcolor=ft.colors.GREEN_800
            )
            self.page.snack_bar.open = True
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.CircleAvatar(foreground_image_url=active_user.get("avatar_url"), radius=18),
                ft.Column([
                    ft.Text(active_user.get("name"), weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PUBLIC, size=10, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Text("Public", size=10, color=ft.colors.ON_SURFACE_VARIANT)
                        ], spacing=3),
                        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                        border_radius=4,
                        padding=ft.padding.symmetric(2, 4)
                    )
                ], spacing=2)
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    post_input,
                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                    image_input
                ], spacing=10, tight=True),
                width=350,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Post", on_click=submit_post, bgcolor=ft.colors.BLUE_ACCENT_400, color=ft.colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def _handle_story_click(self, story):
        if not self.page:
            return
            
        images = story.get("images", [])
        if not images:
            return
            
        story_user = self.db_manager.get_user(story.get("userId"))
        
        # Display the story image inside a beautiful modal dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.CircleAvatar(foreground_image_url=story_user.get("avatar_url"), radius=16),
                ft.Text(story_user.get("name"), weight=ft.FontWeight.BOLD, size=14)
            ], spacing=8),
            content=ft.Container(
                content=ft.Image(src=images[0].get("url"), fit=ft.ImageFit.CONTAIN),
                width=350,
                height=450,
                bgcolor=ft.colors.BLACK,
                border_radius=8
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def _handle_create_story(self, e):
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Story Creation Feature coming soon!"),
                bgcolor=ft.colors.BLUE_800
            )
            self.page.snack_bar.open = True
            self.page.update()

def get_home_view(db_manager: DatabaseManager):
    return HomeView(db_manager)
