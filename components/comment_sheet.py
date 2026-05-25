import flet as ft
from database.db_manager import DatabaseManager

class CommentSheet(ft.Container):
    def __init__(self, post_id, db_manager: DatabaseManager, on_comment_added=None):
        self.post_id = post_id
        self.db_manager = db_manager
        self.on_comment_added = on_comment_added
        
        post = db_manager.get_post(post_id)
        self.comments = post.get("comments", []) if post else []
        active_user = db_manager.get_active_user()
        avatar_url = active_user.get("avatar_url", "") if active_user else ""

        # Scrollable list for comments
        self.comments_column = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=10
        )
        
        # Populate comments
        self.load_comments()

        # Comment Input field
        self.input_field = ft.TextField(
            hint_text="Write a comment...",
            border_radius=20,
            expand=True,
            content_padding=ft.padding.symmetric(10, 16),
            text_size=13,
            on_submit=self._submit_comment,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_color=ft.colors.TRANSPARENT,
            hint_style=ft.TextStyle(color=ft.colors.ON_SURFACE_VARIANT),
        )

        super().__init__(
            bgcolor=ft.colors.SURFACE,
            border_radius=ft.border_radius.only(top_left=16, top_right=16),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=24),
            height=500,  # Slide-up modal height
        )

        self.content = ft.Column([
            # Sheet Header
            ft.Row([
                ft.Text(f"Comments ({len(self.comments)})", weight=ft.FontWeight.BOLD, size=16),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=lambda e: self.close_sheet()
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
            
            # Scrollable list area
            ft.Container(
                content=self.comments_column,
                expand=True,
                padding=ft.padding.symmetric(vertical=8)
            ),
            
            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
            
            # Input Row (Sticky at the bottom)
            ft.Container(
                content=ft.Row([
                    ft.CircleAvatar(
                        foreground_image_url=avatar_url,
                        radius=16
                    ),
                    self.input_field,
                    ft.IconButton(
                        icon=ft.icons.SEND,
                        icon_color=ft.colors.BLUE_ACCENT_400,
                        icon_size=20,
                        on_click=self._submit_comment
                    )
                ], spacing=8),
                padding=ft.padding.only(top=8)
            )
        ], spacing=10)

    def load_comments(self):
        self.comments_column.controls.clear()
        
        if not self.comments:
            # Empty state
            self.comments_column.controls.append(
                ft.Container(
                    content=ft.Text("No comments yet. Be the first to comment!", italic=True, color=ft.colors.ON_SURFACE_VARIANT),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            return

        for c in self.comments:
            avatar = c.get("avatar_url", "")
            name = c.get("name", "User")
            content = c.get("content", "")
            create_at = c.get("create_at", "Just now")
            
            comment_bubble = ft.Row([
                ft.CircleAvatar(
                    foreground_image_url=avatar,
                    radius=16,
                    alignment=ft.alignment.top_center
                ),
                ft.Expanded(
                    child=ft.Column([
                        # Comment Bubble Container
                        ft.Container(
                            content=ft.Column([
                                ft.Text(name, weight=ft.FontWeight.BOLD, size=12, color=ft.colors.ON_SURFACE),
                                ft.Text(content, size=13, color=ft.colors.ON_SURFACE)
                            ], spacing=2),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            border_radius=12,
                            padding=ft.padding.all(10),
                        ),
                        # Comment Actions Row
                        ft.Row([
                            ft.Text(create_at, size=10, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Text("Like", size=10, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Text("Reply", size=10, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE_VARIANT),
                        ], spacing=12, padding=ft.padding.only(left=4))
                    ], spacing=2)
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=8)
            
            self.comments_column.controls.append(comment_bubble)

    def _submit_comment(self, e):
        text = self.input_field.value.strip()
        if not text:
            return
        
        # Save to DB
        new_comment = self.db_manager.add_comment(self.post_id, text)
        if new_comment:
            self.comments.append(new_comment)
            self.input_field.value = ""
            self.load_comments()
            self.comments_column.update()
            self.input_field.update()
            
            # Callback to refresh main post card comment counter
            if self.on_comment_added:
                self.on_comment_added()
                
            # Scroll to bottom
            self.comments_column.scroll_to(offset=-1, duration=300)

    def close_sheet(self):
        if self.page:
            self.page.bottom_sheet.open = False
            self.page.update()
