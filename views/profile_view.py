import flet as ft
from database.db_manager import DatabaseManager
from components.post_card import PostCard

class ProfileView(ft.Container):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=0, right=0, top=0, bottom=4),
        )
        
        self.scroll_column = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=12
        )
        
        self.content = self.scroll_column
        self.refresh_profile()

    def refresh_profile(self):
        self.scroll_column.controls.clear()
        
        active_user = self.db_manager.get_active_user()
        cover_url = active_user.get("cover_url", "https://cdn.pixabay.com/photo/2015/02/24/15/41/dog-647528__340.jpg")
        avatar_url = active_user.get("avatar_url", "")
        name = active_user.get("name", "Hoàng Vũ")
        sub_name = active_user.get("subName", "")
        intro = active_user.get("introTxt", "")
        
        # 1. Header with Cover and Overlapping Avatar
        cover_img = ft.Image(src=cover_url, height=180, fit=ft.ImageFit.COVER, width=430)
        
        avatar_circle = ft.Container(
            content=ft.CircleAvatar(
                foreground_image_url=avatar_url,
                radius=50,
            ),
            border=ft.border.all(4, ft.colors.SURFACE),
            border_radius=54,
            width=108,
            height=108,
            alignment=ft.alignment.center
        )
        
        header_stack = ft.Stack([
            # Cover photo
            cover_img,
            # Avatar overlapping at the bottom center
            ft.Container(
                content=avatar_circle,
                bottom=0,
                alignment=ft.alignment.bottom_center,
                width=430,
                height=108
            )
        ], height=230)
        
        self.scroll_column.controls.append(header_stack)
        
        # 2. User Name and Bio Info
        name_info = ft.Column([
            ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
            ft.Text(f"({sub_name})" if sub_name else "", size=12, color=ft.colors.ON_SURFACE_VARIANT) if sub_name else ft.Container(),
            ft.Text(intro, size=13, italic=True, color=ft.colors.ON_SURFACE_VARIANT) if intro else ft.Container(),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2, width=430)
        self.scroll_column.controls.append(ft.Container(content=name_info, alignment=ft.alignment.center))
        
        # 3. Action Buttons Row (Add to Story, Edit Profile)
        action_buttons = ft.Row([
            ft.ElevatedButton(
                text="Add to Story",
                icon=ft.icons.ADD,
                bgcolor=ft.colors.BLUE_ACCENT_400,
                color=ft.colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                expand=True,
                on_click=lambda _: self._show_snack("Add to Story clicked!")
            ),
            ft.ElevatedButton(
                text="Edit Profile",
                icon=ft.icons.EDIT,
                bgcolor=ft.colors.SURFACE_VARIANT,
                color=ft.colors.ON_SURFACE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                expand=True,
                on_click=self._open_edit_profile_dialog
            ),
        ], spacing=10, width=410)
        self.scroll_column.controls.append(ft.Container(content=action_buttons, padding=ft.padding.symmetric(horizontal=12)))
        
        self.scroll_column.controls.append(ft.Container(content=ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT), padding=ft.padding.symmetric(horizontal=12)))
        
        # 4. Details List (Live in, Work at, follower count, etc.)
        details = []
        if active_user.get("work_at"):
            details.append(ft.Row([ft.Icon(ft.icons.WORK, size=16, color=ft.colors.ON_SURFACE_VARIANT), ft.Text(f"Works at {active_user.get('work_at')}", size=12)]))
        if active_user.get("live_in"):
            details.append(ft.Row([ft.Icon(ft.icons.HOME, size=16, color=ft.colors.ON_SURFACE_VARIANT), ft.Text(f"Lives in {active_user.get('live_in')}", size=12)]))
        if active_user.get("from"):
            details.append(ft.Row([ft.Icon(ft.icons.LOCATION_ON, size=16, color=ft.colors.ON_SURFACE_VARIANT), ft.Text(f"From {active_user.get('from')}", size=12)]))
        if active_user.get("follower"):
            details.append(ft.Row([ft.Icon(ft.icons.RSS_FEED, size=16, color=ft.colors.ON_SURFACE_VARIANT), ft.Text(f"Followed by {active_user.get('follower'):,} people", size=12)]))
            
        details_column = ft.Column(details, spacing=8)
        self.scroll_column.controls.append(ft.Container(content=details_column, padding=ft.padding.symmetric(horizontal=16)))
        
        # 5. Photos Row Grid (Simulate grid)
        photos = [
            "https://cdn.pixabay.com/photo/2015/02/24/15/41/dog-647528__340.jpg",
            "https://gamek.mediacdn.vn/2019/10/20/photo-1-1571521922264714072244.jpg",
            "https://www.ebtc.ie/wp-content/uploads/2017/10/bigstock-Autumn-Fall-scene-Beautiful-150998720.jpg",
            "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__340.jpg"
        ]
        
        photo_images = [ft.Image(src=p, fit=ft.ImageFit.COVER, width=80, height=80, border_radius=6) for p in photos]
        photos_row = ft.Row(photo_images, spacing=10)
        photos_container = ft.Column([
            ft.Text("Photos", weight=ft.FontWeight.BOLD, size=14),
            photos_row
        ], spacing=6)
        
        self.scroll_column.controls.append(ft.Container(content=photos_container, padding=ft.padding.symmetric(horizontal=16)))
        self.scroll_column.controls.append(ft.Container(content=ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT), padding=ft.padding.symmetric(horizontal=12)))
        
        # 6. Own Posts
        self.scroll_column.controls.append(
            ft.Container(
                content=ft.Text("My Posts", weight=ft.FontWeight.BOLD, size=14),
                padding=ft.padding.symmetric(horizontal=16)
            )
        )
        
        posts = self.db_manager.get_posts()
        my_posts = [p for p in posts if p.get("userId") == active_user.get("id")]
        
        if not my_posts:
            self.scroll_column.controls.append(
                ft.Container(
                    content=ft.Text("You haven't posted anything yet.", italic=True, color=ft.colors.ON_SURFACE_VARIANT),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for mp in my_posts:
                post_card = PostCard(mp, self.db_manager, on_post_updated=self.refresh_profile)
                # Wrap inside a container to give padding
                self.scroll_column.controls.append(ft.Container(content=post_card, padding=ft.padding.symmetric(horizontal=8)))
                
        if self.page:
            self.update()

    def _show_snack(self, message):
        if self.page:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.BLUE_800)
            self.page.snack_bar.open = True
            self.page.update()

    def _open_edit_profile_dialog(self, e):
        if not self.page:
            return
            
        active_user = self.db_manager.get_active_user()
        
        name_input = ft.TextField(label="Name", value=active_user.get("name"), border_radius=8)
        bio_input = ft.TextField(label="Bio", value=active_user.get("introTxt"), border_radius=8, multiline=True)
        work_input = ft.TextField(label="Work at", value=active_user.get("work_at"), border_radius=8)
        
        def save_profile(_):
            active_user["name"] = name_input.value.strip()
            active_user["introTxt"] = bio_input.value.strip()
            active_user["work_at"] = work_input.value.strip()
            self.db_manager.save_db()
            
            self.page.dialog.open = False
            self.refresh_profile()
            self._show_snack("Profile updated successfully!")

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Edit Profile Details"),
            content=ft.Container(
                content=ft.Column([
                    name_input,
                    bio_input,
                    work_input
                ], spacing=10, tight=True),
                width=300
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Save", on_click=save_profile, bgcolor=ft.colors.BLUE_ACCENT_400, color=ft.colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

def get_profile_view(db_manager: DatabaseManager):
    return ProfileView(db_manager)
