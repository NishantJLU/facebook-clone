import flet as ft
from database.db_manager import DatabaseManager
from components.post_card import PostCard

class GroupsView(ft.Container):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.selected_category_id = None
        self.search_query = ""
        
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
        )
        
        # Scrollable View
        self.scroll_column = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=10
        )
        
        self.content = self.scroll_column
        self.refresh_groups()

    def refresh_groups(self, e=None):
        self.scroll_column.controls.clear()
        
        # 1. Search & Filter Bar
        search_field = ft.TextField(
            hint_text="Search groups...",
            border_radius=20,
            content_padding=ft.padding.symmetric(0, 16),
            height=36,
            text_size=13,
            prefix_icon=ft.icons.SEARCH,
            on_change=self._handle_search,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_color=ft.colors.TRANSPARENT,
            hint_style=ft.TextStyle(color=ft.colors.ON_SURFACE_VARIANT),
        )
        
        self.scroll_column.controls.append(
            ft.Row([
                ft.Text("Groups", size=20, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.icons.SETTINGS, icon_size=18)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        
        self.scroll_column.controls.append(search_field)
        
        # 2. Action buttons row
        action_buttons = ft.Row([
            ft.Container(
                content=ft.Text("Your Groups", size=12, weight=ft.FontWeight.W_600),
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=ft.padding.symmetric(8, 12),
                border_radius=15,
                on_click=lambda _: self._show_snack("Viewing Your Groups")
            ),
            ft.Container(
                content=ft.Text("Discover", size=12, weight=ft.FontWeight.W_600),
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=ft.padding.symmetric(8, 12),
                border_radius=15,
                on_click=lambda _: self._show_snack("Opening Group Discovery")
            ),
            ft.Container(
                content=ft.Text("+ Create", size=12, weight=ft.FontWeight.W_600),
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=ft.padding.symmetric(8, 12),
                border_radius=15,
                on_click=self._open_create_group_dialog
            ),
        ], spacing=8)
        self.scroll_column.controls.append(action_buttons)
        
        # 3. Categories Horizontal Scroll
        categories = self.db_manager.get_group_categories()
        category_controls = []
        
        # "All" category button
        all_active = self.selected_category_id is None
        category_controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.icons.ALL_INCLUSIVE, color=ft.colors.WHITE if all_active else ft.colors.BLUE_500),
                        bgcolor=ft.colors.BLUE_500 if all_active else ft.colors.SURFACE_VARIANT,
                        width=44,
                        height=44,
                        border_radius=22,
                        alignment=ft.alignment.center
                    ),
                    ft.Text("All", size=10, weight=ft.FontWeight.BOLD if all_active else ft.FontWeight.NORMAL)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                on_click=lambda _: self._select_category(None)
            )
        )
        
        for cat in categories:
            cat_id = cat.get("id")
            is_active = self.selected_category_id == cat_id
            category_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Image(src=cat.get("avatar_url"), fit=ft.ImageFit.COVER, width=44, height=44, border_radius=22),
                            border=ft.border.all(2, ft.colors.BLUE_ACCENT_400) if is_active else None,
                            border_radius=22,
                        ),
                        ft.Text(cat.get("name"), size=10, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    on_click=lambda _, cid=cat_id: self._select_category(cid)
                )
            )
            
        categories_container = ft.Container(
            content=ft.Row(category_controls, scroll=ft.ScrollMode.ADAPTIVE, spacing=16),
            padding=ft.padding.symmetric(vertical=4)
        )
        self.scroll_column.controls.append(categories_container)
        
        self.scroll_column.controls.append(ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT))
        self.scroll_column.controls.append(ft.Text("Recent Activity", weight=ft.FontWeight.BOLD, size=14))
        
        # 4. Group Feed List
        group_posts = self.db_manager.get_group_posts()
        
        # Apply filters
        filtered_posts = []
        for gp in group_posts:
            # Search filter
            content_text = gp.get("content", "").lower()
            group_name = gp.get("group", {}).get("name", "").lower()
            if self.search_query and (self.search_query not in content_text and self.search_query not in group_name):
                continue
                
            # Category filter (mock lookup - we map groups to category)
            # In db.json, categories have list of group IDs: cat.groups = [{groupId: 1}]
            if self.selected_category_id:
                cat = next((c for c in categories if c.get("id") == self.selected_category_id), None)
                if cat:
                    group_ids = [g.get("groupId") for g in cat.get("groups", [])]
                    if gp.get("group", {}).get("id") not in group_ids:
                        continue
            
            filtered_posts.append(gp)

        if not filtered_posts:
            self.scroll_column.controls.append(
                ft.Container(
                    content=ft.Text("No group posts found matching filters.", italic=True, color=ft.colors.ON_SURFACE_VARIANT),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
        else:
            for gp in filtered_posts:
                post_card = PostCard(gp, self.db_manager, on_post_updated=self.refresh_groups)
                self.scroll_column.controls.append(post_card)
                
        if self.page:
            self.update()

    def _select_category(self, category_id):
        self.selected_category_id = category_id
        self.refresh_groups()

    def _handle_search(self, e):
        self.search_query = e.control.value.strip().lower()
        self.refresh_groups()

    def _show_snack(self, message):
        if self.page:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.BLUE_800)
            self.page.snack_bar.open = True
            self.page.update()

    def _open_create_group_dialog(self, e):
        if not self.page:
            return
            
        group_name_input = ft.TextField(
            label="Group Name",
            hint_text="Enter a name for your group",
            border_radius=8,
            autofocus=True
        )
        
        def submit_group(_):
            name = group_name_input.value.strip()
            if not name:
                return
            
            # Add a mock new group (just append to the list in memory)
            groups = self.db_manager.data.setdefault("groups", [])
            new_id = max([g.get("id", 0) for g in groups]) + 1 if groups else 1
            new_group = {
                "id": new_id,
                "name": name,
                "avatar_url": "https://www.hiltonbuffalothunder.com/uploads/1/0/6/8/106825145/adobestock-72120130-2-orig_orig.jpeg"
            }
            groups.append(new_group)
            self.db_manager.save_db()
            
            self.page.dialog.open = False
            self.refresh_groups()
            self._show_snack(f"Group '{name}' created successfully!")

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Create New Group"),
            content=ft.Container(content=group_name_input, width=300, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Create", on_click=submit_group, bgcolor=ft.colors.BLUE_ACCENT_400, color=ft.colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

def get_groups_view(db_manager: DatabaseManager):
    return GroupsView(db_manager)
