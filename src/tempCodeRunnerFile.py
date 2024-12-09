        if self in self.page.overlay:
            self.page.overlay.remove(self)  # Remove dialog from overlay
        self.open = False  # Ensure dialog is closed
        self.page.update()  # Refresh the page