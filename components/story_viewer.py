import flet as ft
import time
import threading

class StoryViewer(ft.Container):
    def __init__(self, story, user, on_close):
        super().__init__()
        self.story = story
        self.user = user
        self.on_close = on_close
        self.images = story.get("images", [])
        self.current_index = 0
        self.is_running = True
        self.paused = False
        
        self.width = 350
        self.height = 600
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = 16
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        
        # Progress Bars
        self.progress_bars = []
        for _ in self.images:
            self.progress_bars.append(
                ft.ProgressBar(
                    value=0,
                    bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                    color=ft.Colors.WHITE,
                    height=2,
                    expand=True
                )
            )
            
        self.progress_row = ft.Row(self.progress_bars, spacing=4)
        
        # Image Control
        self.image_control = ft.Image(
            src=self.images[self.current_index].get("url"),
            fit=ft.BoxFit.COVER,
            expand=True
        )
        
        # Header
        self.header = ft.Row([
            ft.Row([
                ft.CircleAvatar(foreground_image_src=user.get("avatar_url"), radius=16),
                ft.Column([
                    ft.Text(user.get("name"), weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.WHITE),
                    ft.Text(self.images[self.current_index].get("create_at", "Just now"), size=11, color=ft.Colors.WHITE70),
                ], spacing=0)
            ], spacing=8),
            ft.IconButton(ft.Icons.CLOSE, icon_color=ft.Colors.WHITE, on_click=self._close)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Navigation Areas
        self.left_nav = ft.GestureDetector(
            content=ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT),
            on_tap=self._prev_story,
            expand=True
        )
        self.right_nav = ft.GestureDetector(
            content=ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT),
            on_tap=self._next_story,
            expand=True
        )
        
        self.content = ft.Stack([
            self.image_control,
            ft.Container(
                content=ft.Column([
                    ft.Container(self.progress_row, padding=ft.Padding.only(top=10, left=10, right=10)),
                    ft.Container(self.header, padding=10),
                ], spacing=0),
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER,
                    end=ft.Alignment.BOTTOM_CENTER,
                    colors=[ft.Colors.with_opacity(0.6, ft.Colors.BLACK), ft.Colors.TRANSPARENT],
                    stops=[0, 0.4]
                )
            ),
            ft.Row([
                self.left_nav,
                self.right_nav,
            ], expand=True)
        ])
        
    def did_mount(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._run_progress, daemon=True)
        self.thread.start()
        
    def will_unmount(self):
        self.is_running = False

    def _run_progress(self):
        duration = 5.0  # 5 seconds per story
        steps = 50
        step_duration = duration / steps
        
        while self.is_running and self.current_index < len(self.images):
            for i in range(steps + 1):
                if not self.is_running: return
                while self.paused:
                    time.sleep(0.1)
                    if not self.is_running: return
                
                self.progress_bars[self.current_index].value = i / steps
                self.progress_bars[self.current_index].update()
                time.sleep(step_duration)
            
            # Move to next
            if self.current_index < len(self.images) - 1:
                self._next_story(None)
            else:
                self._close(None)
                break

    def _next_story(self, e):
        if self.current_index < len(self.images) - 1:
            # Mark previous as full
            self.progress_bars[self.current_index].value = 1
            self.progress_bars[self.current_index].update()
            
            self.current_index += 1
            self.image_control.src = self.images[self.current_index].get("url")
            self.header.controls[0].controls[1].controls[1].value = self.images[self.current_index].get("create_at", "Just now")
            self.update()
        else:
            self._close(None)

    def _prev_story(self, e):
        if self.current_index > 0:
            # Clear current and previous
            self.progress_bars[self.current_index].value = 0
            self.progress_bars[self.current_index].update()
            
            self.current_index -= 1
            self.progress_bars[self.current_index].value = 0
            self.progress_bars[self.current_index].update()
            
            self.image_control.src = self.images[self.current_index].get("url")
            self.header.controls[0].controls[1].controls[1].value = self.images[self.current_index].get("create_at", "Just now")
            self.update()
        else:
            # Reset current
            self.progress_bars[self.current_index].value = 0
            self.progress_bars[self.current_index].update()

    def _close(self, e):
        self.is_running = False
        if self.on_close:
            self.on_close()
