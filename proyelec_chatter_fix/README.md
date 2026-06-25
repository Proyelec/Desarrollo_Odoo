# proyelec_chatter_fix — Chatter Mention Fix

**Version:** 17.0.1.0.0  
**License:** LGPL-3  
**Depends on:** `mail`

---

## Overview

This module patches the Odoo 17 Discuss/Mail suggestion service to exclude non-internal users from `@mention` autocomplete suggestions. Without this fix, archived internal users and portal users can appear in the mention dropdown, causing confusion and wasted clicks.

---

## What it does

A JavaScript patch is applied to `SuggestionService.prototype.searchPartnerSuggestions` (from `@mail/core/common/suggestion_service`). After the base method returns its list of partner suggestions, the patch filters the results to keep only entries where `user.isInternalUser === true`.

This means:

- Archived internal users are hidden.
- Portal users are hidden.
- Active internal users continue to appear normally.

---

## Technical Details

The patch is a single file:

```
proyelec_chatter_fix/static/src/mention_filter_patch.js
```

It is loaded as part of `web.assets_backend` and uses Odoo's standard `patch` utility from `@web/core/utils/patch`, so it is compatible with future OWL updates as long as the patched method signature does not change.

No Python models or views are modified.

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_chatter_fix --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_chatter_fix --stop-after-init
```

After installation, clear your browser cache (or do a hard reload) so the updated JS bundle is served.
