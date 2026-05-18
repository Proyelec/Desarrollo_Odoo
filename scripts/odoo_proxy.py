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

Security model — WHITELIST (not blacklist):
    Only explicitly allowed methods can be called.
    Anything not in ALLOWED_METHODS is rejected regardless of how it's written.
    This prevents bypass via string concatenation, private methods, or sudo().

Author: Juan David Villasmil — github.com/jdvillasmil/odoo-agent
"""

import sys
import json
import os
import re

# ─────────────────────────────────────────
# SECURITY: Whitelist of allowed ORM methods
# Only these methods can be called — everything else is blocked.
# ─────────────────────────────────────────
ALLOWED_METHODS = {
    # Search and read
    'search',
    'search_count',
    'search_read',
    'read',
    'browse',
    'read_group',
    # Metadata
    'fields_get',
    'default_get',
    'get_views',
    'get_formview_action',
    'check_access_rights',
    'check_access_rule',
    # Recordset manipulation (no writes)
    'mapped',
    'filtered',
    'sorted',
    'exists',
    'ensure_one',
    # Names and display
    'name_search',
    'name_get',
    # Context (safe alone)
    'with_context',
}

# ─────────────────────────────────────────
# SECURITY: Absolutely forbidden — never allowed regardless of context
# ─────────────────────────────────────────
FORBIDDEN_ALWAYS = {
    'create', 'write', 'unlink',
    '_create', '_write', '_unlink',
    'execute', 'execute_kw',
    'sudo', 'with_user',
    'flush', 'flush_model', 'flush_recordset',
    'invalidate_cache', 'invalidate_recordset',
    'copy', 'action_',
    '__import__', 'eval', 'exec',
    'open', 'subprocess', 'os.',
}

MAX_EXPRESSION_LENGTH = 500


def validate_expression(expr):
    """
    Validate expression against whitelist and forbidden patterns.
    Returns (is_valid, error_message).
    """
    if len(expr) > MAX_EXPRESSION_LENGTH:
        return False, f"Expression too long ({len(expr)} chars, max {MAX_EXPRESSION_LENGTH})"

    # Check for absolutely forbidden terms first
    expr_lower = expr.lower()
    for forbidden in FORBIDDEN_ALWAYS:
        if forbidden.lower() in expr_lower:
            return False, f"Forbidden operation detected: '{forbidden}'. This proxy is read-only."

    # Extract all method calls from the expression (words followed by '(')
    method_calls = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', expr)

    # Filter out known safe builtins and common patterns
    safe_builtins = {
        'env', 'True', 'False', 'None', 'int', 'str', 'list',
        'dict', 'tuple', 'len', 'range', 'print', 'isinstance',
    }

    for method in method_calls:
        if method in safe_builtins:
            continue
        if method not in ALLOWED_METHODS:
            return False, (
                f"Method '{method}' is not in the allowed list.\n"
                f"Allowed methods: {', '.join(sorted(ALLOWED_METHODS))}"
            )

    return True, None


def execute_query(expression):
    """Execute an ORM expression and return the result as JSON."""

    # Validate first
    is_valid, error = validate_expression(expression)
    if not is_valid:
        return {
            "error": f"Security validation failed: {error}",
            "allowed_methods": sorted(ALLOWED_METHODS),
        }

    try:
        import odoo
        from odoo import api, SUPERUSER_ID

        db_name = os.environ.get('ODOO_DB')
        if not db_name:
            from odoo.tools import config
            config.parse_config(['--config', '/home/odoo/.config/odoo/odoo.conf'])
            db_name = config.get('db_name')

        if not db_name:
            return {"error": "Database name not found. Set ODOO_DB environment variable."}

        for path in ['/home/odoo/src/odoo', '/home/odoo/src/user']:
            if path not in sys.path:
                sys.path.insert(0, path)

        registry = odoo.registry(db_name)

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Execute with restricted builtins
            result = eval(expression, {"env": env, "__builtins__": {}})

            # Serialize result
            if hasattr(result, '_ids'):
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
            "security": "Read-only. Only whitelisted ORM methods are allowed.",
            "allowed_methods": sorted(ALLOWED_METHODS),
            "examples": [
                "env['sale.order'].search_count([('state','=','sale')])",
                "env['res.partner'].search_count([])",
                "env['sale.order.line'].search_count([('x_studio_ganado','=',True)])",
                "env['product.template'].fields_get(['name','default_code'])",
                "env['sale.order'].search_read([('state','=','sale')], ['name','partner_id'], limit=5)",
            ]
        }, indent=2))
        sys.exit(1)

    expression = sys.argv[1]
    result = execute_query(expression)
    print(json.dumps(result, indent=2, default=str))

    if "error" in result:
        sys.exit(1)


if __name__ == '__main__':
    main()