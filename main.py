import os

os.environ["ERNIE_TOKEN"] = "*************"

from Tools.Gradio.app import (app)

app.launch()