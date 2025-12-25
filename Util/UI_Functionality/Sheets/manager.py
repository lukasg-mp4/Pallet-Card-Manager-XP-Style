from .add import AddRows
from .delete import DeleteRows
from .clear import ClearSheet

class RowManager:
    def __init__(self, app):
        self.app = app
        self.adder = AddRows(app)
        self.deleter = DeleteRows(app)
        self.clearer = ClearSheet(app)

    def prompt_add_rows(self):
        self.adder.execute()

    def prompt_delete_rows(self):
        self.deleter.execute()

    def prompt_clear_sheet(self):
        self.clearer.execute()