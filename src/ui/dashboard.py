import matplotlib.pyplot as plt


class DashboardApp:
    def __init__(self):
        self.pages = []
        self.current_page_idx = 0
        self.fig = plt.figure(figsize=(18, 12))  # default figure size
        # MATPLOT KEYBOARD KI SUNNO 🙉
        self.fig.canvas.mpl_connect(
            'key_press_event', self._on_key)  # hook to keyboard

    def add_new_page(self, title):
        page = {"title": title, "elements": []}
        self.pages.append(page)
        return page

    def add_element(self, page, func, *args, **kwargs):
        page["elements"].append({"func": func, "args": args, "kwargs": kwargs})

    def _render_current_page(self):
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
        if event.key == 'right':
            self.current_page_idx = (
                self.current_page_idx + 1) % len(self.pages)
        elif event.key == 'left':
            self.current_page_idx = (
                self.current_page_idx - 1) % len(self.pages)
        self._render_current_page()
        self.fig.canvas.draw_idle()

    def run(self):
        self._render_current_page()
        plt.show()
