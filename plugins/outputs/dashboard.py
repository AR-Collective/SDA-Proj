"""
Dashboard Application - Multi-page Visualization Framework

Provides a reusable DashboardApp class for creating multi-page interactive
dashboards with keyboard navigation support.
"""

import matplotlib.pyplot as plt


class DashboardApp:
    """
    Multi-page dashboard application with keyboard navigation.

    Supports multiple pages with multiple visualization elements per page.
    Navigate using LEFT/RIGHT arrow keys.
    """

    def __init__(self):
        """Initialize the dashboard application."""
        self.pages = []
        self.current_page_idx = 0
        self.fig = plt.figure(figsize=(18, 12))
        # Hook to keyboard events for navigation
        self.fig.canvas.mpl_connect('key_press_event', self._on_key)

    def add_new_page(self, title):
        """
        Add a new page to the dashboard.

        Args:
            title: Title for the page

        Returns:
            dict: Page object that can be used to add elements
        """
        page = {"title": title, "elements": []}
        self.pages.append(page)
        return page

    def add_element(self, page, func, *args, **kwargs):
        """
        Add a visualization element to a page.

        Args:
            page: Page object to add element to
            func: Function that renders the visualization
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func
        """
        page["elements"].append({"func": func, "args": args, "kwargs": kwargs})

    def _render_current_page(self):
        """Render the current page with all its elements."""
        self.fig.clear()
        page = self.pages[self.current_page_idx]
        self.fig.suptitle(page["title"], fontsize=20, fontweight="bold")

        num_elements = len(page["elements"])
        if num_elements == 0:
            return

        cols = 2 if num_elements > 1 else 1
        rows = (num_elements + 1) // 2

        for i, element in enumerate(page["elements"]):
            ax = self.fig.add_subplot(rows, cols, i + 1)
            element["func"](*element["args"], ax=ax, **element["kwargs"])

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        self.fig.canvas.draw()

    def _on_key(self, event):
        """Handle keyboard events for page navigation."""
        if event.key == 'right':
            self.current_page_idx = (self.current_page_idx + 1) % len(self.pages)
        elif event.key == 'left':
            self.current_page_idx = (self.current_page_idx - 1) % len(self.pages)
        self._render_current_page()
        self.fig.canvas.draw_idle()

    def run(self):
        """Start the dashboard application."""
        self._render_current_page()
        plt.show()
