import flet as ft
import datetime

class ColorsWrapper:
    def __init__(self, enum_class):
        self._enum = enum_class
    def __getattr__(self, name):
        try:
            return getattr(self._enum, name)
        except AttributeError:
            return name.lower().replace('_', '')
    def with_opacity(self, opacity, color):
        val = color.value if hasattr(color, 'value') else color
        return f"{opacity},{val}"

class IconsWrapper:
    def __init__(self, enum_class):
        self._enum = enum_class
    def __getattr__(self, name):
        return getattr(self._enum, name)

class PaddingWrapper:
    def all(self, val):
        return val
    def symmetric(self, horizontal=0, vertical=0):
        return {'horizontal': horizontal, 'vertical': vertical}
    def only(self, left=0, top=0, right=0, bottom=0):
        return {'left': left, 'top': top, 'right': right, 'bottom': bottom}
class AlignmentWrapper:
    def __init__(self, alignment_class):
        self._class = alignment_class
    def __getattr__(self, name):
        return getattr(self._class, name.upper())

class BorderWrapper:
    def __init__(self, original_module):
        self._original_module = original_module
    def all(self, width=1, color=None):
        side = self._original_module.BorderSide(width, color)
        return self._original_module.Border(top=side, bottom=side, left=side, right=side)
    def only(self, top=None, bottom=None, left=None, right=None):
        return self._original_module.Border(top=top, bottom=bottom, left=left, right=right)
    def __getattr__(self, name):
        return getattr(self._original_module, name)

ft.colors = ColorsWrapper(ft.Colors)
ft.icons = IconsWrapper(ft.icons.Icons)
ft.padding = PaddingWrapper()
ft.margin = PaddingWrapper()
ft.alignment = AlignmentWrapper(ft.alignment.Alignment)
ft.border = BorderWrapper(ft.border)

original_circle_avatar_init = ft.CircleAvatar.__init__
def patched_circle_avatar_init(self, *args, **kwargs):
    if "foreground_image_url" in kwargs:
        kwargs["foreground_image_src"] = kwargs.pop("foreground_image_url")
    original_circle_avatar_init(self, *args, **kwargs)
ft.CircleAvatar.__init__ = patched_circle_avatar_init

original_icon_init = ft.Icon.__init__
def patched_icon_init(self, *args, **kwargs):
    if "name" in kwargs:
        kwargs["icon"] = kwargs.pop("name")
    original_icon_init(self, *args, **kwargs)
ft.Icon.__init__ = patched_icon_init
ft.Icon.name = property(fget=lambda self: self.icon, fset=lambda self, val: setattr(self, 'icon', val))

def Expanded(child, expand=True):
    child.expand = expand
    return child
ft.Expanded = Expanded
ft.animation = ft
ft.ImageFit = ft.BoxFit

original_page_prop = ft.Control.page
def patched_page_getter(self):
    try:
        return original_page_prop.fget(self)
    except RuntimeError:
        return None
ft.Control.page = property(fget=patched_page_getter)

def make_button_patch(cls):
    original_init = cls.__init__
    def patched_init(self, *args, **kwargs):
        if 'text' in kwargs:
            kwargs['content'] = kwargs.pop('text')
        original_init(self, *args, **kwargs)
    cls.__init__ = patched_init

make_button_patch(ft.ElevatedButton)
make_button_patch(ft.TextButton)
make_button_patch(ft.OutlinedButton)
make_button_patch(ft.FilledButton)

from database.db_manager import DatabaseManager
from views.home_view import get_home_view
from views.groups_view import get_groups_view
from views.watch_view import get_watch_view
from views.profile_view import get_profile_view
from views.notifications_view import get_notifications_view
from views.menu_view import get_menu_view
from views.search_results_view import get_search_results_view

def main(page: ft.Page):
    page.title = "Facebook Clone"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 0
    page.bgcolor = ft.colors.BLUE_GREY_900  # Desktop background around the phone frame

    # Initialize Database
    db_manager = DatabaseManager()

    # Active Tab State
    active_tab_index = 0

    # Views Cache
    views_cache = {}

    def get_view(index):
        if index in views_cache:
            # Refresh feeds if needed
            view = views_cache[index]
            if hasattr(view, 'refresh_feed'):
                view.refresh_feed()
            elif hasattr(view, 'refresh_groups'):
                view.refresh_groups()
            elif hasattr(view, 'refresh_watch'):
                view.refresh_watch()
            elif hasattr(view, 'refresh_profile'):
                view.refresh_profile()
            elif hasattr(view, 'refresh_notifications'):
                view.refresh_notifications()
            elif hasattr(view, 'refresh_menu'):
                view.refresh_menu()
            return view

        if index == 0:
            views_cache[index] = get_home_view(db_manager)
        elif index == 1:
            views_cache[index] = get_groups_view(db_manager)
        elif index == 2:
            views_cache[index] = get_watch_view(db_manager)
        elif index == 3:
            views_cache[index] = get_profile_view(db_manager)
        elif index == 4:
            views_cache[index] = get_notifications_view(db_manager)
        elif index == 5:
            views_cache[index] = get_menu_view(db_manager, toggle_theme, switch_tab)
            
        return views_cache[index]

    # --- Header Action Callbacks ---
    def handle_search_click(e):
        # Trigger search dialog
        search_input = ft.TextField(
            hint_text="Search Facebook...",
            border_radius=20,
            content_padding=ft.padding.symmetric(0, 16),
            height=40,
            autofocus=True
        )
        
        def run_search(_):
            query = search_input.value.strip()
            if not query: return
            page.dialog.open = False
            
            # Switch view to search results
            main_content_area.content = get_search_results_view(db_manager, query)
            # Deselect all tabs
            for btn in tab_buttons:
                btn.content.controls[0].color = ft.colors.ON_SURFACE_VARIANT
                btn.content.controls[1].visible = False
                btn.update()
            
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Search"),
            content=ft.Container(content=search_input, width=300, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Search", on_click=run_search, bgcolor=ft.colors.BLUE_ACCENT_400, color=ft.colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    def handle_messenger_click(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Messenger chat features are launching soon!"),
            bgcolor=ft.colors.BLUE_800
        )
        page.snack_bar.open = True
        page.update()

    # --- UI Shell Components ---
    # 1. App Bar
    app_bar = ft.Container(
        content=ft.Row([
            ft.Text(
                "facebook",
                color=ft.colors.BLUE_ACCENT_400,
                size=22,
                weight=ft.FontWeight.BOLD,
                style=ft.TextStyle(letter_spacing=-0.5)
            ),
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.SEARCH_ROUNDED,
                    icon_color=ft.colors.ON_SURFACE,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    icon_size=18,
                    width=32,
                    height=32,
                    on_click=handle_search_click
                ),
                ft.IconButton(
                    icon=ft.icons.CHAT_BUBBLE_ROUNDED,
                    icon_color=ft.colors.ON_SURFACE,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    icon_size=18,
                    width=32,
                    height=32,
                    on_click=handle_messenger_click
                )
            ], spacing=8)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        bgcolor=ft.colors.SURFACE,
    )

    # 2. Tabs Bar
    tab_icons = [
        ft.icons.HOME_ROUNDED,
        ft.icons.PEOPLE_ALT_ROUNDED,
        ft.icons.ONDEMAND_VIDEO_ROUNDED,
        ft.icons.ACCOUNT_CIRCLE_ROUNDED,
        ft.icons.NOTIFICATIONS_ROUNDED,
        ft.icons.MENU_ROUNDED
    ]
    
    tab_buttons = []
    
    def on_tab_click(index):
        nonlocal active_tab_index
        active_tab_index = index
        # Update tab button visuals
        for i, btn in enumerate(tab_buttons):
            is_active = (i == index)
            btn.content.controls[0].color = ft.colors.BLUE_ACCENT_400 if is_active else ft.colors.ON_SURFACE_VARIANT
            btn.content.controls[1].visible = is_active
            btn.update()
        # Update view
        main_content_area.content = get_view(index)
        main_content_area.update()

    for idx, icon in enumerate(tab_icons):
        is_active = (idx == active_tab_index)
        btn = ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=ft.colors.BLUE_ACCENT_400 if is_active else ft.colors.ON_SURFACE_VARIANT, size=22),
                ft.Container(height=3, bgcolor=ft.colors.BLUE_ACCENT_400, border_radius=1.5, visible=is_active, width=32)
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=lambda e, i=idx: on_tab_click(i),
            expand=True,
            height=40,
            alignment=ft.alignment.center
        )
        tab_buttons.append(btn)

    tabs_bar = ft.Container(
        content=ft.Row(tab_buttons, spacing=0),
        bgcolor=ft.colors.SURFACE,
        border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT)),
        padding=ft.padding.only(bottom=2)
    )

    # 3. Main Dynamic Content Area
    main_content_area = ft.Container(
        content=get_view(active_tab_index),
        expand=True,
        bgcolor=ft.colors.SURFACE_VARIANT
    )

    # 4. Status Bar Mock (Battery, Wifi, Time, Notch)
    current_time = datetime.datetime.now().strftime("%H:%M")
    status_bar = ft.Container(
        content=ft.Row([
            # Time on the left
            ft.Text(current_time, size=11, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
            # Notch (Dynamic Island) in center
            ft.Container(
                width=90,
                height=16,
                bgcolor=ft.colors.BLACK,
                border_radius=8,
            ),
            # Icons on the right
            ft.Row([
                ft.Icon(ft.icons.SIGNAL_CELLULAR_ALT, size=11, color=ft.colors.ON_SURFACE),
                ft.Icon(ft.icons.WIFI, size=11, color=ft.colors.ON_SURFACE),
                ft.Icon(ft.icons.BATTERY_CHARGING_FULL, size=11, color=ft.colors.ON_SURFACE),
            ], spacing=4)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=16, vertical=4),
        bgcolor=ft.colors.SURFACE,
    )

    # 5. Home Indicator (Bottom phone pill)
    home_indicator = ft.Container(
        content=ft.Container(
            width=120,
            height=4,
            bgcolor=ft.colors.ON_SURFACE_VARIANT,
            border_radius=2
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(bottom=8, top=4),
        bgcolor=ft.colors.SURFACE
    )

    # Assembly: Internal App View
    app_inner = ft.Column([
        status_bar,
        app_bar,
        tabs_bar,
        main_content_area,
        home_indicator
    ], spacing=0, expand=True)

    # Wrap inside Desktop Phone Bezel / Frame
    phone_frame = ft.Container(
        content=app_inner,
        width=400,
        height=820,
        border_radius=32,
        border=ft.border.all(8, ft.colors.BLACK),  # Phone bezel
        bgcolor=ft.colors.SURFACE,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.colors.with_opacity(0.4, ft.colors.BLACK)
        ),
    )

    # Main view structure: Centered phone frame
    main_layout = ft.Container(
        content=phone_frame,
        alignment=ft.alignment.center,
        expand=True
    )

    # --- State Callbacks ---
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = ft.colors.BLUE_GREY_900
        else:
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = ft.colors.BLACK
            
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
            phone_frame.border = ft.border.all(8, ft.colors.BLACK)
            phone_frame.border_radius = 32
            status_bar.visible = True
            home_indicator.visible = True
            
        page.update()

    page.on_resize = handle_resize
    page.add(main_layout)
    
    # Initialize layout once on startup
    handle_resize(None)

if __name__ == "__main__":
    ft.app(target=main)
