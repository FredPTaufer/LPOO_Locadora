import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from views.main_view import JanelaPrincipal

if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()