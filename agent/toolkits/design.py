# agent/toolkits/design.py
from langchain_core.tools import tool

@tool
def get_ui_patterns(framework: str):
    """Retrieve best-practice patterns for React (Tailwind), Android (Compose), or Vanilla."""
    # This is a curated knowledge base for the Designer
    patterns = {
        "react": {
            "layout": "Use Tailwind CSS utility classes. Prefer CSS Grid for complex layouts.",
            "components": "Use Radix UI primitives for accessible components (Dialog, Select, etc.).",
            "styling": "Maintain a consistent 4px/8px spacing scale. Use CSS variables for design tokens."
        },
        "compose": {
            "layout": "Use Box, Column, and Row. Prefer ConstraintLayout only for very complex, flat hierarchies.",
            "components": "Use Material3 components (Scaffold, TopAppBar, FAB).",
            "styling": "Define design tokens in a central Theme.kt. Use ColorScheme and Typography classes."
        },
        "vanilla": {
            "layout": "Use Flexbox and Grid. Minimal dependencies.",
            "styling": "BEM naming convention for CSS. Focus on semantic HTML5 tags."
        }
    }
    return patterns.get(framework.lower(), "General UI best practices: High contrast, 8px grid, accessible interactive elements.")
