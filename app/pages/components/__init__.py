from iommi import Fragment

from app.assets import mathjax_js


class Equations(Fragment):
    """
    A block of text containing LaTeX equations
    """
    class Meta:
        tag = 'p'
        assets = mathjax_js
