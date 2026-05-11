# Proyelec - Chatter Mention Fix

**Version:** 17.0.1.0.0  
**Author:** AIT - Proyelec  
**License:** LGPL-3  
**Category:** Productivity / Mail

## Description

Fixes the `@mention` suggestion behavior in Odoo's Chatter and Discuss by filtering out archived internal users, so they no longer appear as options when mentioning someone.

## Problem

By default, Odoo 17 includes archived users in the `@mention` suggestion list, causing confusion when trying to notify people who are no longer active in the system.

## Solution

Patches the native `SuggestionService` to filter results and show only active internal users.

## Installation

1. Copy the module into your Odoo addons directory
2. Update the module list
3. Install **Proyelec - Chatter Mention Fix**

## Dependencies

- `mail`

## Technical Notes

The fix is applied via a JavaScript patch on `SuggestionService.prototype.searchPartnerSuggestions`. No database models or XML views are modified.
