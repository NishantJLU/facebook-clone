import flet as ft
from database.db_manager import DatabaseManager
from views.marketplace_view import get_marketplace_view

class MenuView(ft.Container):
    def __init__(self, db_manager: DatabaseManager, on_theme_toggle=None, on_tab_switch=None):
        self.db_manager = db_manager
        self.on_theme_toggle = on_theme_toggle
        self.on_tab_switch = on_tab_switch
        
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=12, right=12, top=4, bottom=4),
        )
        
        self.scroll_column = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=14
        )
        
        self.content = self.scroll_column
        self.refresh_menu()

    def refresh_menu(self):
        self.scroll_column.controls.clear()
        
        active_user = self.db_manager.get_active_user()
        avatar_url = active_user.get("avatar_url", "")
        name = active_user.get("name", "User")
        
        # 1. Header
        self.scroll_column.controls.append(
            ft.Row([
                ft.Text("Menu", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.IconButton(ft.icons.SETTINGS, icon_size=18),
                    ft.IconButton(ft.icons.SEARCH, icon_size=18)
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        
        # 2. Profile Card
        profile_card = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(foreground_image_url=avatar_url, radius=18),
                ft.Column([
                    ft.Text(name, weight=ft.FontWeight.BOLD, size=13),
                    ft.Text("See your profile", size=11, color=ft.colors.ON_SURFACE_VARIANT)
                ], spacing=2)
            ], spacing=10),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.SURFACE,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
            on_click=self._handle_profile_click
        )
        self.scroll_column.controls.append(profile_card)

        # 2.5 Account Switcher
        users = self.db_manager.get_users()
        account_items = []
        for user in users[:5]: # Show first 5 users
            if user.get("id") == self.db_manager.active_user_id:
                continue
            account_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(foreground_image_url=user.get("avatar_url"), radius=14),
                        ft.Text(user.get("name"), size=12, weight=ft.FontWeight.W_500),
                    ], spacing=8),
                    padding=ft.padding.symmetric(8, 12),
                    on_click=lambda e, uid=user.get("id"): self._switch_account(uid)
                )
            )
        
        if account_items:
            account_switcher = ft.Container(
                content=ft.Column([
                    ft.Text("Switch Account", size=13, weight=ft.FontWeight.BOLD),
                    ft.Column(account_items, spacing=0)
                ], spacing=8),
                padding=10,
                border_radius=8,
                bgcolor=ft.colors.SURFACE,
                shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
            )
            self.scroll_column.controls.append(account_switcher)
        
        # 3. Grid of shortcuts
        shortcuts = [
            ("Marketplace", ft.icons.STOREFRONT, ft.colors.BLUE_400),
            ("Groups", ft.icons.GROUP, ft.colors.TEAL_400),
            ("Pages", ft.icons.FLAG, ft.colors.ORANGE_400),
            ("Gaming", ft.icons.SPORTS_ESPORTS, ft.colors.CYAN_400),
            ("Memories", ft.icons.HISTORY, ft.colors.AMBER_400),
            ("Saved", ft.icons.BOOKMARK, ft.colors.PURPLE_400),
            ("Events", ft.icons.EVENT, ft.colors.RED_400),
            ("Feeds", ft.icons.DYNAMIC_FEED, ft.colors.LIGHT_BLUE_400)
        ]
        
        grid_items = []
        for label, icon_name, color in shortcuts:
            grid_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(icon_name, color=color, size=20),
                        ft.Text(label, size=11, weight=ft.FontWeight.W_500)
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.colors.SURFACE,
                    border_radius=8,
                    padding=10,
                    width=90,
                    height=70,
                    shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
                    on_click=lambda e, l=label: self._handle_shortcut_click(l)
                )
            )
            
        shortcuts_grid = ft.GridView(
            controls=grid_items,
            runs_count=3,
            max_extent=120,
            spacing=8,
            run_spacing=8,
            expand=False,
            height=160  # Fixed height for grid in scrollview
        )
        
        self.scroll_column.controls.append(
            ft.Column([
                ft.Text("All shortcuts", size=13, weight=ft.FontWeight.BOLD),
                shortcuts_grid
            ], spacing=6)
        )
        
        # 4. Settings Accordion list
        settings_section = ft.Column([
            ft.ExpansionTile(
                title=ft.Text("Help & Support", size=13, weight=ft.FontWeight.W_600),
                leading=ft.Icon(ft.icons.HELP_OUTLINE, size=18),
                controls=[
                    ft.ListTile(title=ft.Text("Help Center", size=12), on_click=lambda _: self._show_snack("Opening Help Center...")),
                    ft.ListTile(title=ft.Text("Support Inbox", size=12), on_click=lambda _: self._show_snack("Opening Support Inbox..."))
                ]
            ),
            ft.ExpansionTile(
                title=ft.Text("Settings & Privacy", size=13, weight=ft.FontWeight.W_600),
                leading=ft.Icon(ft.icons.SETTINGS_OUTLINED, size=18),
                controls=[
                    ft.ListTile(title=ft.Text("Settings", size=12), on_click=lambda _: self._show_snack("Opening Settings...")),
                    # Dark Mode toggle row
                    ft.ListTile(
                        title=ft.Text("Dark Mode", size=12),
                        trailing=ft.Switch(
                            value=False if not self.page else (self.page.theme_mode == ft.ThemeMode.DARK),
                            on_change=self.on_theme_toggle
                        )
                    )
                ]
            )
        ], spacing=2)
        
        self.scroll_column.controls.append(settings_section)
        
        # 5. Logout Button
        logout_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.LOGOUT, color=ft.colors.RED_400, size=16),
                ft.Text("Log Out", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.RED_400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.SURFACE,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.colors.with_opacity(0.08, ft.colors.BLACK)),
            on_click=lambda _: self._show_snack("Logged out successfully (Mock)")
        )
        self.scroll_column.controls.append(logout_btn)
        
        if self.page:
            self.update()

    def _switch_account(self, user_id):
        new_user = self.db_manager.set_active_user(user_id)
        self.refresh_menu()
        self._show_snack(f"Switched to {new_user.get('name')}")
        if self.page:
            self.page.update()

    def _handle_profile_click(self, e):
        # Switch tab to profile
        if self.on_tab_switch:
            self.on_tab_switch(3)  # Profile is tab index 3

    def _handle_shortcut_click(self, label):
        if label == "Groups":
            if self.on_tab_switch:
                self.on_tab_switch(1)  # Groups is tab index 1
        elif label == "Marketplace":
            if self.page:
                self.content = get_marketplace_view(self.db_manager)
                self.update()
        else:
            self._show_snack(f"Opening {label}...")

    def _show_snack(self, message):
        if self.page:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.BLUE_800)
            self.page.snack_bar.open = True
            self.page.update()

def get_menu_view(db_manager: DatabaseManager, on_theme_toggle, on_tab_switch):
    return MenuView(db_manager, on_theme_toggle, on_tab_switch)
