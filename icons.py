from markupsafe import Markup

PRODUCT_ICONS = {
    "box": "<path d=\"M21 8l-9-5-9 5v8l9 5 9-5V8z\"/><path d=\"M3 8l9 5 9-5M12 13v8\"/>",
    "graduation-cap": "<path d=\"M22 9L12 4 2 9l10 5 10-5z\"/><path d=\"M6 11.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5\"/><path d=\"M22 9v6\"/>",
    "wallet": "<path d=\"M3 7a2 2 0 012-2h13v4\"/><path d=\"M3 7v11a2 2 0 002 2h15a1 1 0 001-1V10a1 1 0 00-1-1H5a2 2 0 01-2-2z\"/><circle cx=\"16.5\" cy=\"14.5\" r=\"1\"/>",
    "book": "<path d=\"M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2V5z\"/><path d=\"M4 19a2 2 0 012-2h13\"/>",
    "chart": "<path d=\"M4 20V4M4 20h16\"/><path d=\"M8 16v-5M12 16V8M16 16v-8\"/>",
    "calendar": "<rect x=\"3\" y=\"5\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 10h18M8 3v4M16 3v4\"/>",
    "chat": "<path d=\"M21 12a8 8 0 01-11.5 7.2L4 20l1-4.5A8 8 0 1121 12z\"/>",
    "code": "<path d=\"M8 8l-4 4 4 4M16 8l4 4-4 4M14 5l-4 14\"/>",
    "shield": "<path d=\"M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6l8-3z\"/>",
    "mail": "<rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"2\"/><path d=\"M3 7l9 6 9-6\"/>",
    "globe": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18\"/>",
    "layers": "<path d=\"M12 3l9 5-9 5-9-5 9-5z\"/><path d=\"M3 13l9 5 9-5\"/>",
    "sparkles": "<path d=\"M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z\"/><path d=\"M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16z\"/>",
    "check-circle": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M8 12.5l2.7 2.7L16 9.8\"/>",
    "pencil": "<path d=\"M4 20l1-4L16.5 4.5a2.1 2.1 0 013 3L8 19l-4 1z\"/><path d=\"M14 7l3 3\"/>",
    "home": "<path d=\"M3 11l9-8 9 8\"/><path d=\"M5 10v10h14V10\"/>"
}

UI_ICONS = {
    "arrow-up-right": "<path d=\"M7 17L17 7M8 7h9v9\"/>",
    "arrow-down": "<path d=\"M12 5v14M6 13l6 6 6-6\"/>",
    "menu": "<path d=\"M4 7h16M4 12h16M4 17h16\"/>",
    "close": "<path d=\"M6 6l12 12M18 6L6 18\"/>",
    "chevron-down": "<path d=\"M6 9l6 6 6-6\"/>",
    "check": "<path d=\"M5 12.5l4.5 4.5L19 7.5\"/>",
    "arrow-up": "<path d=\"M12 19V5M6 11l6-6 6 6\"/>"
}

ICONS = {**PRODUCT_ICONS, **UI_ICONS}
ICON_NAMES = list(PRODUCT_ICONS)


def icon(name, cls="icon"):
    body = ICONS.get(name, ICONS["box"])
    return Markup(
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>'
    )


def icon_paths(name):
    return Markup(ICONS.get(name, ICONS["box"]))
