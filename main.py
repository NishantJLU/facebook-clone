import flet as ft
import datetime
import os

class ColorsWrapper:
    def __init__(self, enum_class):
        self._enum = enum_class
    def __getattr__(self, name):
        try:
            return getattr(self._enum, name)
        except AttributeError:
            return None

def main(page: ft.Page):
    # --- Page Config ---
    page.title = "Facebook Clone"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.BLACK
    page.window.width = 450
    page.window.height = 850

    # --- Global Patch for ft.Control.page ---
    original_page_prop = ft.Control.page
    def patched_page_getter(self):
        try:
            return original_page_prop.fget(self)
        except RuntimeError:
            return None
    ft.Control.page = property(fget=patched_page_getter)

    from database.db_manager import DatabaseManager
    from views.home_view import get_home_view
    from views.groups_view import get_groups_view
    from views.watch_view import get_watch_view
    from views.profile_view import get_profile_view
    from views.notifications_view import get_notifications_view
    from views.menu_view import get_menu_view
    from views.search_results_view import get_search_results_view

    db_manager = DatabaseManager()

    # --- State ---
    active_tab_index = 0
    views_cache = {}

    def get_view(index, query=None):
        if query:
            return get_search_results_view(db_manager, query)
            
        if index in views_cache:
            return views_cache[index]
            
        view_map = {
            0: get_home_view,
            1: get_watch_view,
            2: get_groups_view,
            3: get_profile_view,
            4: get_notifications_view,
            5: get_menu_view
        }
        view = view_map[index](db_manager)
        views_cache[index] = view
        return view

    # --- UI Components ---
    main_content_area = ft.Container(
        content=get_view(0),
        expand=True,
        bgcolor=ft.Colors.SURFACE,
    )

    def on_tab_click(index):
        nonlocal active_tab_index
        active_tab_index = index
        
        # Update tab icons (active vs inactive)
        for i, tab in enumerate(tab_row.controls):
            is_active = (i == index)
            tab.content.controls[0].color = ft.Colors.BLUE_600 if is_active else ft.Colors.ON_SURFACE_VARIANT
            # Indicator line at top
            tab.content.controls[1].visible = is_active
            
        main_content_area.content = get_view(index)
        page.update()

    def create_tab(icon_data, index):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon_data, size=24, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height=3, bgcolor=ft.Colors.BLUE_600, width=40, border_radius=3, visible=(index==0))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            expand=True,
            on_click=lambda _: on_tab_click(index)
        )

    tab_row = ft.Row([
        create_tab(ft.Icons.HOME_ROUNDED, 0),
        create_tab(ft.Icons.ONDEMAND_VIDEO_ROUNDED, 1),
        create_tab(ft.Icons.GROUPS_ROUNDED, 2),
        create_tab(ft.Icons.PERSON_OUTLINE_ROUNDED, 3),
        create_tab(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, 4),
        create_tab(ft.Icons.MENU_ROUNDED, 5),
    ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_AROUND)

    # --- Search Mockup ---
    def open_search(e):
        search_input = ft.TextField(
            hint_text="Search Facebook",
            autofocus=True,
            on_submit=lambda e: run_search(e)
        )
        
        def run_search(e):
            query = search_input.value
            if query:
                setattr(page.dialog, 'open', False)
                main_content_area.content = get_view(-1, query)
                page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Search"),
            content=ft.Container(content=search_input, width=300, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(page.dialog, 'open', False) or page.update()),
                ft.Button("Search", on_click=run_search, bgcolor=ft.Colors.BLUE_ACCENT_400, color=ft.Colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    header = ft.Container(
        content=ft.Row([
            ft.Text("facebook", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
            ft.Row([
                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                ft.IconButton(ft.Icons.SEARCH_ROUNDED, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, on_click=open_search),
                ft.IconButton(ft.Icons.MESSAGE_ROUNDED, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
            ], spacing=8)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.only(left=16, right=16, top=8, bottom=8),
        bgcolor=ft.Colors.SURFACE
    )

    # --- System Bar Mockup ---
    current_time = datetime.datetime.now().strftime("%H:%M")
    status_bar = ft.Container(
        content=ft.Row([
            ft.Text(current_time, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
            # Notch (Dynamic Island) in center
            ft.Container(
                width=90,
                height=16,
                bgcolor=ft.Colors.BLACK,
                border_radius=10,
            ),
            ft.Row([
                ft.Icon(ft.Icons.SIGNAL_CELLULAR_4_BAR_ROUNDED, size=12),
                ft.Icon(ft.Icons.WIFI_ROUNDED, size=12),
                ft.Icon(ft.Icons.BATTERY_FULL_ROUNDED, size=12),
            ], spacing=4)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.symmetric(horizontal=24, vertical=6)
    )

    home_indicator = ft.Container(
        width=120,
        height=4,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        border_radius=2,
        margin=ft.Margin.only(bottom=8),
        alignment=ft.Alignment.CENTER
    )

    # --- Main Layout Assembly ---
    content_stack = ft.Column([
        header,
        tab_row,
        ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
        main_content_area
    ], spacing=0, expand=True)

    phone_frame = ft.Container(
        content=ft.Column([
            status_bar,
            content_stack,
            home_indicator
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=400,
        height=820,
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.all(8, ft.Colors.BLACK),
        border_radius=32,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        expand=False
    )

    main_layout = ft.Container(
        content=phone_frame,
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    # --- State Callbacks ---
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = ft.Colors.BLUE_GREY_900
        else:
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = ft.Colors.BLACK

        # Re-build views cache to apply theme changes
        views_cache.clear()

        # Refresh current view
        main_content_area.content = get_view(active_tab_index)
        page.update()

    def switch_tab(index):
        on_tab_click(index)

    # --- Responsive Layout Handling ---
    def handle_resize(e):
        if page.width < 500:
            # Mobile View: Remove phone bezel & frame spacing
            phone_frame.width = None
            phone_frame.height = None
            phone_frame.border = None
            phone_frame.border_radius = 0
            status_bar.visible = False  # Let native status bar handle it
            home_indicator.visible = False
        else:
            # Desktop View: Center within phone mockup
            phone_frame.width = 400
            phone_frame.height = 820
            phone_frame.border = ft.Border.all(8, ft.Colors.BLACK)
            phone_frame.border_radius = 32
            status_bar.visible = True
            home_indicator.visible = True
            
        page.update()

    page.on_resize = handle_resize
    page.add(main_layout)
    
    # Initialize layout once on startup
    handle_resize(None)

if __name__ == "__main__":
    ft.app(main)
