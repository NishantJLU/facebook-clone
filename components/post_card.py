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
            bgcolor=ft.Colors.SURFACE,
            padding=12,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            margin=ft.Margin.only(bottom=8),
            animate_opacity=300,
            animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            opacity=0,
            scale=0.9
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
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            self.actions_row
        ], spacing=8)

    def did_mount(self):
        self.opacity = 1
        self.scale = 1
        self.update()

    def _build_header(self):
        group = self.post.get("group")
        if group:
            name_control = ft.Row([
                ft.Text(self.author_name, weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.ON_SURFACE),
                ft.Icon(ft.Icons.NAVIGATE_NEXT, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(group.get("name"), weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.ON_SURFACE)
            ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            name_control = ft.Text(self.author_name, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.ON_SURFACE)

        return ft.Row([
            # Avatar
            ft.CircleAvatar(
                foreground_image_src=self.author_avatar,
                radius=18
            ),
            # Name + Timestamp
            ft.Column([
                name_control,
                ft.Row([
                    ft.Text(self.post.get("create_at", "Just now"), size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Icon(ft.Icons.PUBLIC, size=11, color=ft.Colors.ON_SURFACE_VARIANT)
                ], spacing=4)
            ], spacing=2, expand=True),
            # More options button
            ft.IconButton(
                icon=ft.Icons.MORE_HORIZ,
                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                icon_size=18,
                on_click=self._show_post_options
            )
        ], spacing=8)

    def _build_content(self):
        text = self.post.get("content", "")
        if not text:
            return ft.Container()
        return ft.Container(
            content=ft.Text(text, size=13, color=ft.Colors.ON_SURFACE),
            padding=ft.Padding.only(bottom=4)
        )

    def _build_attachment(self):
        images = self.post.get("images", [])
        single_img = self.post.get("image")
        
        if not images and not single_img:
            return ft.Container()
            
        if images:
            # Multi-image carousel
            image_controls = []
            for img_url in images:
                image_controls.append(
                    ft.Container(
                        content=ft.Image(
                            src=img_url,
                            fit=ft.BoxFit.COVER,
                            width=350,
                            height=250,
                        ),
                        border_radius=4,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    )
                )
            
            return ft.Container(
                content=ft.Row(
                    image_controls,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=8,
                ),
                padding=ft.Padding.only(bottom=4)
            )
        else:
            # Single image fallback
            return ft.Container(
                content=ft.Image(
                    src=single_img,
                    fit=ft.BoxFit.COVER,
                    border_radius=4,
                    width=400,
                    height=250,
                ),
                border_radius=4,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.Alignment.CENTER
            )

    def _build_counters(self):
        # Reactions sum
        reactions = self.post.get("reactions", {"like": 0, "love": 0, "haha": 0, "wow": 0, "sad": 0, "angry": 0})
        total_reacts = sum(reactions.values())
        
        # Comments count
        comments = self.post.get("comments", [])
        total_comments = len(comments)
        
        # Determine which reaction icons to show (top 3 non-zero)
        active_reactions = [(k, v) for k, v in reactions.items() if v > 0]
        active_reactions.sort(key=lambda x: x[1], reverse=True)
        top_reactions = active_reactions[:3]
        
        reaction_icons = []
        reaction_config = {
            "like": (ft.Icons.THUMB_UP, ft.Colors.BLUE_500),
            "love": (ft.Icons.FAVORITE, ft.Colors.RED_500),
            "haha": (ft.Icons.SENTIMENT_VERY_SATISFIED, ft.Colors.AMBER_400),
            "wow": (ft.Icons.EMOJI_EMOTIONS, ft.Colors.AMBER_400),
            "sad": (ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.AMBER_400),
            "angry": (ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.ORANGE_700)
        }
        
        for react_type, _ in top_reactions:
            icon_name, color = reaction_config.get(react_type, (ft.Icons.THUMB_UP, ft.Colors.BLUE_500))
            reaction_icons.append(
                ft.Container(
                    content=ft.Icon(icon_name, size=10, color=ft.Colors.WHITE),
                    bgcolor=color,
                    shape=ft.BoxShape.CIRCLE,
                    padding=3
                )
            )
        
        if not reaction_icons:
             reaction_icons.append(
                ft.Container(
                    content=ft.Icon(ft.Icons.THUMB_UP, size=10, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_500,
                    shape=ft.BoxShape.CIRCLE,
                    padding=3
                )
            )

        reacts_row = ft.Row(reaction_icons + [
            ft.Text(str(total_reacts), size=11, color=ft.Colors.ON_SURFACE_VARIANT)
        ], spacing=-4 if len(reaction_icons) > 1 else 4)
        
        comments_row = ft.Row([
            ft.Text(f"{total_comments} comments", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(" • ", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text("1 share", size=11, color=ft.Colors.ON_SURFACE_VARIANT)
        ], spacing=2)
        
        return ft.Row([
            reacts_row,
            comments_row
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_actions(self):
        # We need stateful buttons
        self.like_button_text = ft.Text(
            "Like", 
            size=12, 
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SURFACE_VARIANT if not self.is_liked else ft.Colors.BLUE_ACCENT_400
        )
        self.like_button_icon = ft.Icon(
            ft.Icons.THUMB_UP_OUTLINED if not self.is_liked else ft.Icons.THUMB_UP, 
            color=ft.Colors.ON_SURFACE_VARIANT if not self.is_liked else ft.Colors.BLUE_ACCENT_400, 
            size=16
        )

        self.like_button = ft.GestureDetector(
            content=ft.Container(
                content=ft.Row([
                    self.like_button_icon,
                    self.like_button_text
                ], spacing=6),
                padding=ft.Padding.symmetric(vertical=8, horizontal=12),
                border_radius=4,
            ),
            on_tap=self._handle_like,
            on_long_press_start=self._show_reaction_picker,
            mouse_cursor="pointer"
        )
        
        comment_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=ft.Colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Comment", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_comment_click
        )
        
        share_button = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SHARE, color=ft.Colors.ON_SURFACE_VARIANT, size=16),
                ft.Text("Share", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=6),
            on_click=self._handle_share
        )
        
        return ft.Row([
            self.like_button,
            comment_button,
            share_button
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    def _show_reaction_picker(self, e: ft.LongPressStartEvent):
        if not self.page: return

        reaction_config = [
            ("Like", ft.Icons.THUMB_UP, ft.Colors.BLUE_500, "like"),
            ("Love", ft.Icons.FAVORITE, ft.Colors.RED_500, "love"),
            ("Haha", ft.Icons.SENTIMENT_VERY_SATISFIED, ft.Colors.AMBER_400, "haha"),
            ("Wow", ft.Icons.EMOJI_EMOTIONS, ft.Colors.AMBER_400, "wow"),
            ("Sad", ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.AMBER_400, "sad"),
            ("Angry", ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.ORANGE_700, "angry"),
        ]

        reactions = []
        for name, icon, color, r_type in reaction_config:
            reactions.append(
                ft.Container(
                    content=ft.Icon(icon, color=color, size=24),
                    padding=8,
                    on_click=lambda e, rt=r_type: self._handle_reaction_select(rt),
                    tooltip=name,
                    shape=ft.BoxShape.CIRCLE,
                    animate=ft.Animation(200, "decelerate"),
                    on_hover=lambda e: setattr(e.control, 'scale', 1.3 if e.data == "true" else 1) or e.control.update()
                )
            )

        picker = ft.Container(
            content=ft.Row(reactions, spacing=4, tight=True),
            bgcolor=ft.Colors.SURFACE,
            border_radius=30,
            padding=ft.Padding.symmetric(vertical=4, horizontal=8),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
            left=e.global_x - 100 if hasattr(e, "global_x") else 50,
            top=e.global_y - 80 if hasattr(e, "global_y") else 50,
            animate_opacity=200,
            offset=ft.Offset(0, -0.5),
            animate_offset=ft.Animation(300, "decelerate")
        )

        def close_picker(e):
            self.page.overlay.remove(picker)
            self.page.update()

        # Add a transparent layer to close picker when clicking outside
        dismiss_layer = ft.GestureDetector(
            content=ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT),
            on_tap=close_picker
        )
        
        self.page.overlay.append(dismiss_layer)
        self.page.overlay.append(picker)
        self.page.update()
        
        # Store for closing
        self._reaction_picker = picker
        self._dismiss_layer = dismiss_layer

    def _handle_reaction_select(self, reaction_type):
        if hasattr(self, "_reaction_picker"):
            self.page.overlay.remove(self._dismiss_layer)
            self.page.overlay.remove(self._reaction_picker)
            
        self.is_liked = True
        self.db_manager.like_post(self.post.get("id"), reaction_type=reaction_type, increment=True)
        
        # Update button visuals based on reaction
        reaction_config = {
            "like": (ft.Icons.THUMB_UP, ft.Colors.BLUE_ACCENT_400, "Like"),
            "love": (ft.Icons.FAVORITE, ft.Colors.RED_500, "Love"),
            "haha": (ft.Icons.SENTIMENT_VERY_SATISFIED, ft.Colors.AMBER_400, "Haha"),
            "wow": (ft.Icons.EMOJI_EMOTIONS, ft.Colors.AMBER_400, "Wow"),
            "sad": (ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.AMBER_400, "Sad"),
            "angry": (ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.ORANGE_700, "Angry")
        }
        
        icon, color, text = reaction_config.get(reaction_type)
        self.like_button_icon.icon = icon
        self.like_button_icon.color = color
        self.like_button_text.value = text
        self.like_button_text.color = color
        
        self._refresh_counters()

    def _handle_like(self, e):
        self.is_liked = not self.is_liked
        # Update db.json
        reaction_type = "like"
        self.db_manager.like_post(self.post.get("id"), reaction_type=reaction_type, increment=self.is_liked)
        
        # Reset to default like button visuals
        if self.is_liked:
            self.like_button_icon.icon = ft.Icons.THUMB_UP
            self.like_button_icon.color = ft.Colors.BLUE_ACCENT_400
            self.like_button_text.value = "Like"
            self.like_button_text.color = ft.Colors.BLUE_ACCENT_400
        else:
            self.like_button_icon.icon = ft.Icons.THUMB_UP_OUTLINED
            self.like_button_icon.color = ft.Colors.ON_SURFACE_VARIANT
            self.like_button_text.value = "Like"
            self.like_button_text.color = ft.Colors.ON_SURFACE_VARIANT
        
        self._refresh_counters()

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
                bgcolor=ft.Colors.GREEN_800
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
                    ft.TextButton("Delete Post", on_click=delete_post, icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400),
                    ft.TextButton("Cancel", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update())
                ]
            )
            self.page.dialog.open = True
            self.page.update()
