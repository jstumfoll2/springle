
from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.floatlayout import FloatLayout

from kivy.core.window import Window
from kivy.metrics import dp

from lib.SpringleWidget import SpringleWidget
from lib.TextOverlay import TextOverlay
from lib.OptionsPanel import OptionsPanel

from lib.SpringleProfiler import initialize_profiler

class SpringleApp(MDApp):
    """Main application class"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"
        
        # Create root layout
        root = FloatLayout()
        
        # Initialize profiler
        self.profiler = initialize_profiler(self)
        
        # Create text overlay as a separate top-level widget
        self.text_overlay = TextOverlay()
        
        # Create navigation drawer
        self.nav_drawer = MDNavigationDrawer(
            radius=(0, 16, 16, 0),
            elevation=4,
            width=dp(320),
            enable_swiping=False,
            type="modal"
        )
        
        # Create and add springle widget
        self.springle_widget = SpringleWidget()
        
        # Add options panel to drawer
        self.options_panel = OptionsPanel(self.springle_widget)
        self.nav_drawer.add_widget(self.options_panel)
        
        
        root.add_widget(self.text_overlay)
        root.add_widget(self.nav_drawer)
        root.add_widget(self.springle_widget)
        
        # Set initial window size (width, height)
        Window.bind(on_resize=self._on_resize)
        Window.size = (1024, 1024) 

        return root
    
    def _on_resize(self, instance, width, height):
        """Handle window resize events"""
        # print(f"App Window resized to: {width}x{height}")  # Debug print

        # Manually trigger window resize handling to initialize the circle system correctly
        self.springle_widget._on_resize(None, *Window.size)  # Call the resize handler manually
        
        self.profiler = initialize_profiler(self)
    
    def on_pause(self):
        """Handle app pause"""
        return True
    
    def on_resume(self):
        """Handle app resume"""
        pass

if __name__ == '__main__':
    SpringleApp().run()