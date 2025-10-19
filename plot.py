# visualize_graph.py
import graphviz
from PIL import Image

with open("graph.dot") as f:
    dot_source = f.read()

g = graphviz.Source(dot_source)
g.render("graph", format="png", cleanup=True)

# Mostrar na tela (sem abrir nada externo)
Image.open("graph.png").show()

