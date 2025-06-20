"""
Theme management for GitTTY.
Provides predefined color schemes and theme management functionality.
"""

class Theme:
    """Base theme class that defines the color scheme interface."""
    
    def __init__(self, name, colors):
        self.name = name
        self.colors = colors
    
    def get_color(self, color_name):
        """Get a specific color from the theme."""
        return self.colors.get(color_name, "")


# Predefined themes
THEMES = {
    "default": Theme("Default", {
        "header": "\033[95m",
        "info": "\033[94m", 
        "cyan": "\033[96m",
        "success": "\033[92m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }),
    
    "dark": Theme("Dark", {
        "header": "\033[38;5;141m",      # Purple
        "info": "\033[38;5;75m",         # Light Blue
        "cyan": "\033[38;5;87m",         # Bright Cyan
        "success": "\033[38;5;120m",     # Bright Green
        "warning": "\033[38;5;220m",     # Gold
        "error": "\033[38;5;196m",       # Bright Red
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }),
    
    "light": Theme("Light", {
        "header": "\033[38;5;55m",       # Dark Purple
        "info": "\033[38;5;25m",         # Dark Blue
        "cyan": "\033[38;5;30m",         # Dark Cyan
        "success": "\033[38;5;28m",      # Dark Green
        "warning": "\033[38;5;130m",     # Dark Orange
        "error": "\033[38;5;124m",       # Dark Red
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }),
    
    "cyberpunk": Theme("Cyberpunk", {
        "header": "\033[38;5;201m",      # Hot Pink
        "info": "\033[38;5;51m",         # Neon Cyan
        "cyan": "\033[38;5;14m",         # Bright Cyan
        "success": "\033[38;5;46m",      # Neon Green
        "warning": "\033[38;5;226m",     # Electric Yellow
        "error": "\033[38;5;9m",         # Bright Red
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }),
    
    "ocean": Theme("Ocean", {
        "header": "\033[38;5;24m",       # Deep Blue
        "info": "\033[38;5;39m",         # Sky Blue
        "cyan": "\033[38;5;45m",         # Aqua
        "success": "\033[38;5;36m",      # Teal
        "warning": "\033[38;5;214m",     # Orange
        "error": "\033[38;5;160m",       # Coral Red
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }),
    
    "forest": Theme("Forest", {
        "header": "\033[38;5;22m",       # Forest Green
        "info": "\033[38;5;34m",         # Green
        "cyan": "\033[38;5;43m",         # Light Green
        "success": "\033[38;5;40m",      # Bright Green
        "warning": "\033[38;5;178m",     # Tan
        "error": "\033[38;5;88m",        # Dark Red
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }),
    
    "mono": Theme("Monochrome", {
        "header": "\033[1m",             # Bold only
        "info": "\033[0m",               # Normal
        "cyan": "\033[0m",               # Normal
        "success": "\033[1m",            # Bold
        "warning": "\033[4m",            # Underline
        "error": "\033[1;4m",            # Bold + Underline
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    })
}


def get_available_themes():
    """Get a list of all available theme names."""
    return list(THEMES.keys())


def get_theme(theme_name):
    """Get a theme by name. Returns default theme if not found."""
    return THEMES.get(theme_name, THEMES["default"])


def get_theme_preview(theme_name):
    """Get a preview string showing what the theme looks like."""
    theme = get_theme(theme_name)
    return (
        f"{theme.get_color('header')}■ Header{theme.get_color('reset')} "
        f"{theme.get_color('info')}■ Info{theme.get_color('reset')} "
        f"{theme.get_color('success')}■ Success{theme.get_color('reset')} "
        f"{theme.get_color('warning')}■ Warning{theme.get_color('reset')} "
        f"{theme.get_color('error')}■ Error{theme.get_color('reset')}"
    )
