{
    "name": "Proyelec - Chatter Mention Fix",
    "version": "17.0.1.0.0",
    "category": "Productivity/Mail",
    "summary": "Hide archived internal users from @mention suggestions in Chatter/Discuss",
    "depends": ["mail"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "proyelec_chatter_fix/static/src/mention_filter_patch.js",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
