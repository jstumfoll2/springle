from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

class ScrollableOptionsPanel(ScrollView):
    """Scrollable container for options panel"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False  # Only vertical scrolling
        self.bar_width = dp(4)
        self.scroll_type = ['bars']
        self.bar_color = [0.7, 0.7, 0.7, 0.9]
        self.bar_inactive_color = [0.7, 0.7, 0.7, 0.2]
        self.do_scroll = True
        self.scroll_distance = dp(10)
        
    """Scrollable container for options panel"""
    def on_touch_down(self, touch):
        # Check if touch is on a slider
        for child in self.children[0].children:  # content's children
            if isinstance(child, MDBoxLayout) and len(child.children) > 1:
                slider = child.children[0]  # The slider is the first child
                if hasattr(slider, 'cursor_pos') and slider.collide_point(*slider.to_widget(*touch.pos)):
                    # If touch is on slider, disable scrolling temporarily
                    self.do_scroll_y = False
                    return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # Re-enable scrolling
        self.do_scroll_y = True
        return super().on_touch_up(touch)    
        