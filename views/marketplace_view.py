import flet as ft
from database.db_manager import DatabaseManager

class MarketplaceView(ft.Container):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(expand=True, padding=12)
        self.db_manager = db_manager
        
        self.scroll_column = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            spacing=12,
        )
        self.content = self.scroll_column
        self.refresh_marketplace()

    def refresh_marketplace(self):
        self.scroll_column.controls.clear()
        
        # Header
        self.scroll_column.controls.append(
            ft.Row([
                ft.Text("Marketplace", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.IconButton(ft.Icons.PERSON_ROUNDED, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                    ft.IconButton(ft.Icons.SEARCH_ROUNDED, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST)
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        
        # Categories
        categories = [
            ("Vehicles", ft.Icons.DIRECTIONS_CAR),
            ("Rentals", ft.Icons.HOUSE),
            ("Electronics", ft.Icons.DEVICES),
            ("Free", ft.Icons.FAVORITE)
        ]
        cat_row = ft.Row([
            ft.Container(
                content=ft.Row([ft.Icon(icon, size=16), ft.Text(label, size=12, weight=ft.FontWeight.W_500)], spacing=4),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                padding=ft.Padding.symmetric(vertical=6, horizontal=12),
                border_radius=20,
            ) for label, icon in categories
        ], scroll=ft.ScrollMode.HIDDEN)
        self.scroll_column.controls.append(cat_row)
        
        # Product Grid
        products = self.db_manager.get_products()
        grid_items = []
        for product in products:
            grid_items.append(self._build_product_card(product))
            
        product_grid = ft.GridView(
            controls=grid_items,
            runs_count=2,
            max_extent=200,
            child_aspect_ratio=0.8,
            spacing=10,
            run_spacing=10,
        )
        self.scroll_column.controls.append(product_grid)
        
        if self.page:
            self.update()

    def _build_product_card(self, product):
        img_url = product.get("images", [""])[0]
        price = product.get("price", 0)
        title = product.get("title", "Product")
        
        return ft.Container(
            content=ft.Column([
                ft.Image(src=img_url, fit=ft.BoxFit.COVER, expand=True, border_radius=ft.BorderRadius.only(top_left=8, top_right=8)),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"₫{price:,}", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text(title, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=2),
                    padding=8
                )
            ], spacing=0),
            bgcolor=ft.Colors.SURFACE,
            border_radius=8,
            on_click=lambda e: self._show_product_details(product)
        )

    def _show_product_details(self, product):
        if not self.page: return
        
        def close_sheet(e):
            self.page.bottom_sheet.open = False
            self.page.update()

        self.page.bottom_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Product Details", weight=ft.FontWeight.BOLD, size=18),
                        ft.IconButton(ft.Icons.CLOSE, on_click=close_sheet)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Image(src=product.get("images", [""])[0], height=250, fit=ft.BoxFit.COVER, border_radius=8),
                    ft.Text(product.get("title"), weight=ft.FontWeight.BOLD, size=20),
                    ft.Text(f"${product.get('price'):,}", color=ft.Colors.BLUE_ACCENT_400, weight=ft.FontWeight.BOLD, size=18),
                    ft.Text(f"Status: {product.get('statusTxt')}", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Divider(),
                    ft.Text("Description", weight=ft.FontWeight.BOLD),
                    ft.Text(product.get("description"), size=14),
                    ft.Row([
                        ft.Button("Message Seller", icon=ft.Icons.CHAT, expand=True),
                        ft.IconButton(ft.Icons.SHARE, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST)
                    ], spacing=10)
                ], spacing=12, scroll=ft.ScrollMode.ALWAYS, tight=True),
                padding=20,
                bgcolor=ft.Colors.SURFACE,
                border_radius=ft.BorderRadius.only(top_left=16, top_right=16)
            ),
            is_scroll_controlled=True,
        )
        self.page.bottom_sheet.open = True
        self.page.update()

def get_marketplace_view(db_manager: DatabaseManager):
    return MarketplaceView(db_manager)
