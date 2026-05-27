import flet as ft
from database.db_manager import DatabaseManager

class Composer(ft.Container):
    def __init__(self, db_manager: DatabaseManager, on_write_post=None):
        self.db_manager = db_manager
        self.on_write_post = on_write_post
        active_user = db_manager.get_active_user()
        avatar_url = active_user.get("avatar_url", "") if active_user else ""
        
        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            padding=12,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )
        
        self.content = ft.Column([
            # Top row: Avatar + input text trigger
            ft.Row([
                ft.CircleAvatar(
                    foreground_image_src=avatar_url,
                    radius=20
                ),
                ft.Container(
                    content=ft.Text(
                        "What's on your mind?",
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        size=14
                    ),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=20,
                    padding=ft.Padding.symmetric(vertical=10, horizontal=16),
                    on_click=on_write_post,
                    alignment=ft.Alignment.CENTER_LEFT,
                    expand=True
                )
            ], spacing=10),
            
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            
            # Bottom row: Action Buttons (Live, Photo, Feeling/Activity)
            ft.Row([
                # Live Video
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.VIDEOCAM, color=ft.Colors.RED_400, size=18),
                        ft.Text("Live", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE)
                    ], spacing=4),
                    on_click=lambda _: self.show_mock_alert("Live Streaming feature is starting soon!")
                ),
                # Photo/Video
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PHOTO_LIBRARY, color=ft.Colors.GREEN_400, size=18),
                        ft.Text("Photo", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE)
                    ], spacing=4),
                    on_click=on_write_post
                ),
                # Room / Feeling
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INSERT_EMOTICON, color=ft.Colors.AMBER_400, size=18),
                        ft.Text("Feeling", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE)
                    ], spacing=4),
                    on_click=lambda _: self.show_mock_alert("Feelings & Activities popup is coming soon!")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=8)

    def show_mock_alert(self, message):
        # We will show a snackbar or alert
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                action="OK",
                bgcolor=ft.Colors.BLUE_800
            )
            self.page.snack_bar.open = True
            self.page.update()
