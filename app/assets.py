from typing import Any, Dict

from iommi import Asset

mathjax_js: Dict[str, Any] = dict(
    mathjax_inline = Asset.js(
        attrs__src='/static/js/mathjax-inline.js'
    ),
    mathjax_js = Asset.js(
        attrs__id="MathJax-script",
        attrs__src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
        attrs__async=True,
    )
)
