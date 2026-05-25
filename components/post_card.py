import flet as ft
from database.db_manager import DatabaseManager
from components.comment_sheet import CommentSheet

class PostCard(ft.Container):
    def __init__(self, post, db_manager: DatabaseManager, on_post_updated=None):
        self.post = post
        self.db_manager = db_manager
        self.on_post_updated = on_post_updated
        
        # Look up author info
        author_id = post.get("userId")
        author = db_manager.get_user(author_id)
        self.author_name = author.get("name", "Facebook User") if author else "Facebook User"
        self.author_avatar = author.get("avatar_url", "") if author else ""
        
        # Check initial like state (simulate session-based or toggle-based like)
        self.is_liked = False
        
        super().__init__(
            bgcolor=ft.colors.SURFACE,
            padding=12,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
            margin=ft.margin.only(bottom=8),
        )
        
        # Build components
        self.header_row = self._build_header()
        self.content_text = self._build_content()
        self.attachment_image = self._build_attachment()
        self.counters_row = self._build_counters()
        self.actions_row = self._build_actions()
        
        # Assemble
        self.content = ft.Column([
            self.header_row,
            self.content_text,
            self.attachment_image,
            ft.Container(height=4),
            self.counters_row,
            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
            self.actions_row
        ], spacing=8)

    def _build_header(self):
        group = self.post.get("group")
        if group:
            name_control = ft.Row([
                ft.Text(self.author_name, weight=ft.FontWeight.BOLD, size=12, color=ft.colors.ON_SURFACE),
                ft.Icon(ft.icons.NAVIGATE_NEXT, size=14, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Text(group.get("name"), weight=ft.FontWeight.BOLD, size=12, color=ft.colors.ON_SURFACE)
            ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            name_control = ft.Text(self.author_name, weight=ft.FontWeight.BOLD, size=13, color=ft.colors.ON_SURFACE)

        return ft.Row([
            # Avatar
            ft.CircleAvatar(
                foreground_image_url=self.author_avatar,
                radius=18
            ),
            # Name + Timestamp
            ft.Expanded(
                child=ft.Column([
                    name_control,
                    ft.Row([
                        ft.Text(self.post.get("create_at", "Just now"), size=11, color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Icon(ft.icons.PUBLIC, size=11, color=ft.colors.ON_SURFACE_VARIANT)
                    ], spacing=4)
                ], spacing=2)
            ),
            # More options button
            ft.IconButton(
                icon=ft.icons.MORE_HORIZ,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
                icon_size=18,
                on_click=self._show_post_options
            )
        ], spacing=8)

    def _build_content(self):
        text = self.post.get("content", "")
        if not text:
            return ft.Container()
        return ft.Container(
            content=ft.Text(text, size=13, color=ft.colors.ON_SURFACE),
            padding=ft.padding.only(bottom=4)
        )

    def _build_attachment(self):
        img_url = self.post.get("image")
        if not img_url:
            return ft.Container()
        return ft.Container(
            content=ft.Image(
                src=img_url,
                fit=ft.ImageFit.COVER,
                border_radius=4,
                width=400,
                height=250,
            ),
            border_radius=4,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            alignment=ft.alignment.center
        )

    def _build_counters(self):
        # Reactions sum
        reactions = self.post.get("reactions", {"like": 0, "love": 0, "haha": 0})
        total_reacts = sum(reactions.values())
        
        # Comments count
        comments = self.post.get("comments", [])
        total_comments = len(comments)
        
        reacts_row = ft.Row([
            # Like Circle
            ft.Container(
                content=ft.Icon(ft.icons.THUMB_UP, size=10, color=ft.colors.WHITE),
                bgcolor=ft.colors.BLUE_500,
                shape=ft.BoxShape.CIRCLE,
                padding=3
            ),
            # Heart Circle
            ft.Container(
                content=ft.Icon(ft.icons.FAVORITE, size=10, color=ft.colors.WHITE),
                bgcolor=ft.colors.RED_500,
                shape=ft.BoxShape.CIRCLE,
                padding=3
            ) if total_reacts > 5 else ft.Container(),
            ft.Text(str(total_reacts), size=11, color=ft.colors.ON_SURFACE_VARIANT)
        ], spacing=4)
        
        comments_row = ft.Row([
            ft.Text(f"{total_comments} comments", size=11, color=ft.colors.ON_SURFACE_VARIANT),
            ft.Text(" • ", size=11, color=ft.colors.ON_SURFACE_VARIANT),
            ft.Text("1 share", size=11, color=ft.colors.ON_SURFACE_VARIANT)
        ], spacing=2)
        
        return ft.Row([
            reacts_row,
            comments_row
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_actions(self):
        # We need stateful buttons
        self.like_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(
                    ft.icons.THUMB_UP_OUTLINED if not self.is_liked else ft.icons.THUMB_UP, 
                    color=ft.colors.ON_SURFACE_VARIANT if not self.is_liked else ft.colors.BLUE_ACCENT_400, 
                    size=16
                ),
                ft.Text(
                    "Like", 
                    size=12, 
                    weight=ft.FontWeight.W_500,
                    color=ft.colors.ON_SURFACE_VARIANT if not self.is_liked else ft.colors.BLUE_ACCENT_400
                )
            ], spacing=6),
            on_click=self._handle_like
        )
        
        comment_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE, color=ft.colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Comment", size=12, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_comment_click
        )
        
        share_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.icons.SHARE, color=ft.colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Share", size=12, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_share
        )
        
        return ft.Row([
            self.like_button,
            comment_button,
            share_button
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    def _handle_like(self, e):
        self.is_liked = not self.is_liked
        # Update db.json
        self.db_manager.like_post(self.post.get("id"), reaction_type="like", increment=self.is_liked)
        
        # Refresh self counters
        # We recreate the counter row and replace it
        self.content.controls[3] = self._build_counters()
        # We recreate the button state
        self.like_button.content.controls[0].name = ft.icons.THUMB_UP if self.is_liked else ft.icons.THUMB_UP_OUTLINED
        self.like_button.content.controls[0].color = ft.colors.BLUE_ACCENT_400 if self.is_liked else ft.colors.ON_SURFACE_VARIANT
        self.like_button.content.controls[1].color = ft.colors.BLUE_ACCENT_400 if self.is_liked else ft.colors.ON_SURFACE_VARIANT
        
        self.update()
        if self.on_post_updated:
            self.on_post_updated()

    def _handle_comment_click(self, e):
        if self.page:
            # Open comment sheet inside page bottom sheet
            self.page.bottom_sheet = CommentSheet(
                post_id=self.post.get("id"),
                db_manager=self.db_manager,
                on_comment_added=self._refresh_counters
            )
            self.page.bottom_sheet.open = True
            self.page.update()

    def _refresh_counters(self):
        # Refresh counters from the updated db
        updated_post = self.db_manager.get_post(self.post.get("id"))
        if updated_post:
            self.post = updated_post
            self.content.controls[3] = self._build_counters()
            self.update()
            if self.on_post_updated:
                self.on_post_updated()

    def _handle_share(self, e):
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Post shared successfully to your timeline!"),
                action="OK",
                bgcolor=ft.colors.GREEN_800
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _show_post_options(self, e):
        if self.page:
            def delete_post(_):
                # Simple mock delete
                posts = self.db_manager.data.get("posts", [])
                for p in posts:
                    if p.get("id") == self.post.get("id"):
                        posts.remove(p)
                        self.db_manager.data["posts"] = posts
                        self.db_manager.save_db()
                        break
                self.page.dialog.open = False
                self.page.update()
                if self.on_post_updated:
                    self.on_post_updated()

            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Post Options"),
                content=ft.Text("What would you like to do with this post?"),
                actions=[
                    ft.TextButton("Delete Post", on_click=delete_post, icon=ft.icons.DELETE, icon_color=ft.colors.RED_400),
                    ft.TextButton("Cancel", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update())
                ]
            )
            self.page.dialog.open = True
            self.page.update()
