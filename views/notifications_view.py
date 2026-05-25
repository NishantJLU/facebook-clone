import flet as ft
from database.db_manager import DatabaseManager

class NotificationsView(ft.Container):
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
        self.refresh_notifications()

    def refresh_notifications(self):
        self.scroll_column.controls.clear()
        
        # Header title
        self.scroll_column.controls.append(
            ft.Row([
                ft.Text("Notifications", size=20, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.icons.SEARCH, icon_size=18)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        
        notifications = self.db_manager.get_notifications()
        if not notifications:
            self.scroll_column.controls.append(
                ft.Container(
                    content=ft.Text("You have no notifications.", italic=True, color=ft.colors.ON_SURFACE_VARIANT),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
            return

        for notif in notifications:
            # Resolve user details
            sender_id = notif.get("userId")
            sender = self.db_manager.get_user(sender_id)
            sender_name = sender.get("name", "Someone") if sender else "Someone"
            sender_avatar = sender.get("avatar_url", "") if sender else ""
            
            # Formulate notification text based on type
            notif_type = notif.get("type", 1)
            action_buttons = None
            
            if notif_type == 1:
                # Group post
                group_id = notif.get("groupId")
                groups = self.db_manager.get_groups()
                group = next((g for g in groups if g.get("id") == group_id), None)
                group_name = group.get("name", "Group") if group else "Group"
                notif_text = f"{sender_name} posted in the group {group_name}."
                icon_name = ft.icons.GROUP
                icon_color = ft.colors.BLUE_400
            elif notif_type == 2:
                # Comment
                notif_text = f"{sender_name} commented on your post."
                icon_name = ft.icons.COMMENT
                icon_color = ft.colors.GREEN_400
            elif notif_type == 3:
                # Friend request
                notif_text = f"{sender_name} sent you a friend request."
                icon_name = ft.icons.PERSON_ADD
                icon_color = ft.colors.PURPLE_400
                
                # Render Accept/Decline action buttons
                notif_id = notif.get("id")
                action_buttons = self._build_friend_request_actions(notif_id)
            else:
                # Standard like
                notif_text = f"{sender_name} liked your photo."
                icon_name = ft.icons.THUMB_UP
                icon_color = ft.colors.BLUE_ACCENT_400

            # Render Notification Card
            notif_card = self._build_notif_card(notif, sender_avatar, notif_text, icon_name, icon_color, action_buttons)
            self.scroll_column.controls.append(notif_card)
            
        if self.page:
            self.update()

    def _build_notif_card(self, notif, avatar_url, text, icon_name, icon_color, action_buttons=None):
        is_seen = notif.get("isSeen", True)
        
        # Blue dot if unseen
        blue_dot = ft.Container(
            width=8,
            height=8,
            border_radius=4,
            bgcolor=ft.colors.BLUE_ACCENT_400,
            alignment=ft.alignment.center
        ) if not is_seen else ft.Container()
        
        card = ft.Container(
            bgcolor=ft.colors.with_opacity(0.06, ft.colors.BLUE_ACCENT_100) if not is_seen else ft.colors.SURFACE,
            padding=10,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
            on_click=lambda e, n=notif: self._mark_as_read(n),
        )
        
        # Avatar with overlapping small type icon
        avatar_stack = ft.Stack([
            ft.CircleAvatar(foreground_image_url=avatar_url, radius=20),
            ft.Container(
                content=ft.Icon(icon_name, size=10, color=ft.colors.WHITE),
                bgcolor=icon_color,
                shape=ft.BoxShape.CIRCLE,
                padding=2,
                bottom=-2,
                right=-2
            )
        ], width=40, height=40)
        
        # Layout
        body = ft.Column([
            ft.Row([
                avatar_stack,
                ft.Expanded(
                    child=ft.Column([
                        ft.Text(text, size=12, color=ft.colors.ON_SURFACE, weight=ft.FontWeight.W_500 if not is_seen else ft.FontWeight.NORMAL),
                        ft.Text(notif.get("create_at", "Just now"), size=10, color=ft.colors.ON_SURFACE_VARIANT)
                    ], spacing=2)
                ),
                blue_dot
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=4)
        
        if action_buttons:
            body.controls.append(
                ft.Container(
                    content=action_buttons,
                    padding=ft.padding.only(left=50)
                )
            )
            
        card.content = body
        return card

    def _build_friend_request_actions(self, notif_id):
        # We will return a Row with Accept and Decline buttons
        buttons_row = ft.Row()
        
        def accept_request(_):
            self.db_manager.accept_friend_request(notif_id)
            buttons_row.controls.clear()
            buttons_row.controls.append(ft.Text("Friends", color=ft.colors.ON_SURFACE_VARIANT, size=11, italic=True))
            buttons_row.update()
            self._show_snack("Friend request accepted!")
            
        def decline_request(_):
            # Just remove it
            notifications = self.db_manager.get_notifications()
            for n in notifications:
                if n.get("id") == notif_id:
                    notifications.remove(n)
                    break
            self.db_manager.save_db()
            self.refresh_notifications()
            self._show_snack("Friend request declined.")

        buttons_row.controls.extend([
            ft.ElevatedButton(
                text="Confirm", 
                on_click=accept_request, 
                bgcolor=ft.colors.BLUE_ACCENT_400, 
                color=ft.colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                height=26
            ),
            ft.ElevatedButton(
                text="Delete", 
                on_click=decline_request, 
                bgcolor=ft.colors.SURFACE_VARIANT, 
                color=ft.colors.ON_SURFACE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                height=26
            )
        ])
        
        return buttons_row

    def _mark_as_read(self, notif):
        if not notif.get("isSeen"):
            notif["isSeen"] = True
            self.db_manager.save_db()
            self.refresh_notifications()

    def _show_snack(self, message):
        if self.page:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.BLUE_800)
            self.page.snack_bar.open = True
            self.page.update()

def get_notifications_view(db_manager: DatabaseManager):
    return NotificationsView(db_manager)
