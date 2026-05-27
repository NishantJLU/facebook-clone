import flet as ft
from database.db_manager import DatabaseManager
from components.post_card import PostCard

class SearchResultsView(ft.Container):
    def __init__(self, db_manager: DatabaseManager, query: str):
        super().__init__(expand=True, padding=12)
        self.db_manager = db_manager
        self.query = query.lower()
        
        self.results_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=12)
        self.content = self.results_column
        self._perform_search()

    def _perform_search(self):
        self.results_column.controls.clear()
        
        # 1. People
        users = self.db_manager.get_users()
        matching_users = [u for u in users if self.query in u.get("name", "").lower()]
        
        if matching_users:
            self.results_column.controls.append(ft.Text("People", weight=ft.FontWeight.BOLD, size=16))
            for user in matching_users:
                self.results_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.CircleAvatar(foreground_image_url=user.get("avatar_url"), radius=20),
                            ft.Column([
                                ft.Text(user.get("name"), weight=ft.FontWeight.BOLD),
                                ft.Text(f"{user.get('live_in', 'Facebook')} User", size=12, color=ft.colors.ON_SURFACE_VARIANT)
                            ], spacing=2),
                            ft.ElevatedButton("Add Friend", icon=ft.icons.PERSON_ADD, scale=0.8)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10,
                        bgcolor=ft.colors.SURFACE,
                        border_radius=8
                    )
                )
        
        # 2. Posts
        posts = self.db_manager.get_posts()
        matching_posts = [p for p in posts if self.query in p.get("content", "").lower()]
        
        if matching_posts:
            self.results_column.controls.append(ft.Text("Posts", weight=ft.FontWeight.BOLD, size=16))
            for post in matching_posts:
                self.results_column.controls.append(PostCard(post, self.db_manager))
                
        if not matching_users and not matching_posts:
            self.results_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, size=50, color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Text(f"No results found for '{self.query}'", color=ft.colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )

def get_search_results_view(db_manager: DatabaseManager, query: str):
    return SearchResultsView(db_manager, query)
