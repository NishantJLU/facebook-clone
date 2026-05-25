import flet as ft
from database.db_manager import DatabaseManager

class StoryCard(ft.Container):
    def __init__(self, story, db_manager: DatabaseManager, on_story_click=None):
        user = db_manager.get_user(story.get("userId"))
        user_name = user.get("name", "User") if user else "User"
        avatar_url = user.get("avatar_url", "") if user else ""
        
        # Get the first image url from the story list
        images = story.get("images", [])
        story_image = images[0].get("url") if images else "https://images.unsplash.com/photo-1506744038136-46273834b3fb"
        
        super().__init__(
            width=100,
            height=160,
            border_radius=12,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=lambda e: on_story_click(story) if on_story_click else None,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.with_opacity(0.15, ft.colors.BLACK)),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
        
        # Visual contents
        self.content = ft.Stack([
            # Story Image Cover
            ft.Image(
                src=story_image,
                fit=ft.ImageFit.COVER,
                width=100,
                height=160
            ),
            # Dark bottom gradient overlay
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.colors.TRANSPARENT, ft.colors.with_opacity(0.65, ft.colors.BLACK)]
                ),
                width=100,
                height=160
            ),
            # User Avatar (Top-left, blue border if unviewed)
            ft.Container(
                content=ft.CircleAvatar(
                    foreground_image_url=avatar_url,
                    radius=16,
                ),
                top=8,
                left=8,
                border=ft.border.all(2, ft.colors.BLUE_ACCENT_400),
                border_radius=18
            ),
            # User Name (Bottom-left)
            ft.Container(
                content=ft.Text(
                    user_name,
                    color=ft.colors.WHITE,
                    size=10,
                    weight=ft.FontWeight.W_600,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                bottom=8,
                left=8,
                right=8
            )
        ])
        
        # Micro-animation on hover
        self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        # Scale card up slightly
        self.scale = 1.03 if e.data == "true" else 1.0
        self.update()


class CreateStoryCard(ft.Container):
    def __init__(self, db_manager: DatabaseManager, on_create_click=None):
        active_user = db_manager.get_active_user()
        avatar_url = active_user.get("avatar_url", "") if active_user else ""
        
        super().__init__(
            width=100,
            height=160,
            border_radius=12,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=on_create_click,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.with_opacity(0.15, ft.colors.BLACK)),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
        
        self.content = ft.Stack([
            # Top half: user avatar
            ft.Image(
                src=avatar_url,
                fit=ft.ImageFit.COVER,
                width=100,
                height=110
            ),
            # Bottom half: white or dark grey background container
            ft.Container(
                content=ft.Column([
                    ft.Container(height=4),
                    ft.Text(
                        "Create\nStory",
                        color=ft.colors.BLUE_ACCENT_400,
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.colors.SURFACE_VARIANT,
                width=100,
                height=50,
                bottom=0,
            ),
            # Blue Plus Icon overlapping the border
            ft.Container(
                content=ft.Icon(
                    name=ft.icons.ADD,
                    color=ft.colors.WHITE,
                    size=16
                ),
                bgcolor=ft.colors.BLUE_ACCENT_400,
                border=ft.border.all(2, ft.colors.SURFACE_VARIANT),
                border_radius=15,
                width=24,
                height=24,
                bottom=38,
                left=38,
            )
        ])
        
        self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        self.scale = 1.03 if e.data == "true" else 1.0
        self.update()


def get_stories_row(db_manager: DatabaseManager, on_story_click=None, on_create_story=None):
    stories = db_manager.get_stories()
    cards = [CreateStoryCard(db_manager, on_create_click=on_create_story)]
    
    for s in stories:
        cards.append(StoryCard(s, db_manager, on_story_click=on_story_click))
        
    return ft.Row(
        controls=cards,
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
