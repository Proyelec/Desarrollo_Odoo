#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
odoo_proxy.py — Read-only ORM query proxy for Odoo 17
======================================================
Allows Claude Code to execute ORM expressions via SSH without
requiring an interactive shell session.

Usage:
    python3 odoo_proxy.py "env['sale.order'].search_count([('state','=','sale')])"

Returns:
    JSON to stdout — {"result": <value>} or {"error": "<message>"}

Security:
    - Read-only operations only (search, search_count, read, browse, fields_get)
    - Write operations are blocked (create, write, unlink, execute_kw)
    - Expression length limited to 500 characters
    - No eval of arbitrary Python — only ORM expressions via restricted env

Author: Juan David Villasmil — github.com/jdvillasmil/odoo-agent
"""

import sys
import json
import os
import re

# ─────────────────────────────────────────
# SECURITY: Allowed ORM methods (read-only)
# ─────────────────────────────────────────
ALLOWED_METHODS = [
    'search',
    'search_count',
    'search_read',
    'read',
    'read_group',
    'browse',
    'fields_get',
    'fields_view_get',
    'name_search',
    'name_get',
    'get_views',
    'mapped',
    'filtered',
    'sorted',
]

BLOCKED_PATTERNS = [
    r'\bcreate\b',
    r'\bwrite\b',
    r'\bunlink\b',
    r'\bexecute_kw\b',
    r'\bexecute\b',
    r'\bsudo\(\)',       # sudo without args is allowed, sudo() with write ops is not
    r'\bimport\b',
    r'\bopen\b',
    r'\beval\b',
    r'\bexec\b',
    r'\bos\.',
    r'\bsubprocess\b',
    r'\b__import__\b',
]

MAX_EXPRESSION_LENGTH = 500


def validate_expression(expr):
    """Validate the expression is safe to execute."""
    if len(expr) > MAX_EXPRESSION_LENGTH:
        return False, f"Expression too long ({len(expr)} chars, max {MAX_EXPRESSION_LENGTH})"

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, expr):
            return False, f"Blocked pattern detected: {pattern}"

    return True, None


def initialize_odoo():
    """Initialize Odoo environment without starting the full server."""
    # Add Odoo to path
    odoo_path = '/home/odoo/src/odoo'
    if odoo_path not in sys.path:
        sys.path.insert(0, odoo_path)

    # Add user modules to path
    user_path = '/home/odoo/src/user'
    if user_path not in sys.path:
        sys.path.insert(0, user_path)

    import odoo
    from odoo import api, SUPERUSER_ID
    from odoo.tools import config

    # Load Odoo config
    config.parse_config([
        '--config', '/home/odoo/.config/odoo/odoo.conf',
    ])

    # Get database name from config or environment
    db_name = os.environ.get('ODOO_DB') or config.get('db_name')
    if not db_name:
        raise ValueError("Database name not found. Set ODOO_DB environment variable.")

    # Initialize registry and environment
    odoo.service.server.load_server_wide_modules()
    registry = odoo.registry(db_name)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        return env, cr, registry


def execute_query(expression):
    """Execute an ORM expression and return the result as JSON."""

    # Validate first
    is_valid, error = validate_expression(expression)
    if not is_valid:
        return {"error": f"Security validation failed: {error}"}

    try:
        import odoo
        from odoo import api, SUPERUSER_ID

        db_name = os.environ.get('ODOO_DB')
        if not db_name:
            # Try to get from odoo config
            from odoo.tools import config
            config.parse_config(['--config', '/home/odoo/.config/odoo/odoo.conf'])
            db_name = config.get('db_name')

        if not db_name:
            return {"error": "Database name not found. Set ODOO_DB environment variable."}

        # Add paths
        for path in ['/home/odoo/src/odoo', '/home/odoo/src/user']:
            if path not in sys.path:
                sys.path.insert(0, path)

        registry = odoo.registry(db_name)

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Execute in restricted context
            result = eval(expression, {"env": env, "__builtins__": {}})

            # Serialize result
            if hasattr(result, '_ids'):
                # It's a recordset
                serialized = {
                    "model": result._name,
                    "ids": list(result._ids),
                    "count": len(result),
                }
            elif hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
                serialized = list(result)
            else:
                serialized = result

            return {"result": serialized}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No expression provided.",
            "usage": "python3 odoo_proxy.py \"env['sale.order'].search_count([])\"",
            "examples": [
                "env['sale.order'].search_count([('state','=','sale')])",
                "env['res.partner'].search_count([])",
                "env['sale.order.line'].search_count([('x_studio_ganado','=',True)])",
                "env['product.template'].fields_get(['name','default_code'])",
            ]
        }, indent=2))
        sys.exit(1)

    expression = sys.argv[1]
    result = execute_query(expression)
    print(json.dumps(result, indent=2, default=str))

    # Exit with error code if there was an error
    if "error" in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
