# proyelec_salas — Meeting Room Privacy Extension

**Version:** 17.0.1.0.0  
**Author:** Contables Boyer  
**License:** LGPL-3  
**Depends on:** `room`, `mail`, `web_gantt`

---

## Overview

This module extends Odoo 17 Enterprise's native `room` module (Meeting Rooms) to add privacy controls, internal attendees, and a meeting agenda field. It was built to replace Lark's meeting room booking functionality while respecting the company's privacy requirements: users should only see that a room is reserved, not who it's for or what it's about, unless they are directly involved.

---

## Features

### Privacy Control
- Bookings marked as **Private** show as `"Reservada"` (Reserved) in all views for users without access.
- Users who **can see full details**: meeting organizer, invited attendees, and users with the **Leader / Management** group.
- Users without access see only: room name, date/time, and `"Reservada"` as the title.
- The **Edit button** is hidden in the calendar and Gantt popovers for users without access.

### New Fields on `room.booking`
| Field | Type | Description |
|---|---|---|
| `is_private` | Boolean | Marks the booking as private. Default: `True` |
| `attendee_ids` | Many2many → `res.users` | Internal Odoo users invited to the meeting |
| `description` | Text | Agenda or meeting description |
| `can_see_details` | Computed Boolean | Whether the current user can see full details |

### Internal Notifications
When a booking is created or modified, all attendees receive an internal Odoo notification (chatter message) with the meeting details: room, date, time, and agenda.

### Access Control
- Users can only **edit or delete their own bookings**.
- Leaders can edit and delete any booking.
- All internal users can **read** all bookings (required to display room availability in the calendar).

---

## Security Groups

Two custom groups are defined under the category **"Salas de Reunión Proyelec"**:

| Group | XML ID | Description |
|---|---|---|
| Usuario | `proyelec_salas.group_room_booking_user` | Can create and edit own bookings. Sees "Reservada" for private bookings of others. |
| Líder / Gerencia | `proyelec_salas.group_room_booking_leader` | Sees full details of all bookings. Can edit and delete any booking. |

### ⚠️ Important: Group Assignment After Installation

These groups are **not assigned automatically** to existing users. After installing the module, you must assign groups manually from:

**Settings → Users & Companies → Users → [Select User] → Meeting Rooms Proyelec section**

Or run the following in the Odoo shell to assign the base group to all internal users at once:

```python
group_user = env.ref('proyelec_salas.group_room_booking_user')
usuarios_internos = env['res.users'].search([
    ('share', '=', False),
    ('active', '=', True),
])
group_user.write({'users': [(4, u.id) for u in usuarios_internos]})
env.cr.commit()
```

Then manually promote specific users (managers, team leads) to **Líder / Gerencia** from the UI.

### ⚠️ Important: Native `room` Module Group

All users who need access to the Meeting Rooms app must also have the native Odoo group `room.group_room_manager`. Assign it to all internal users with:

```python
group_room = env.ref('room.group_room_manager')
usuarios_internos = env['res.users'].search([
    ('share', '=', False),
    ('active', '=', True),
])
group_room.write({'users': [(4, u.id) for u in usuarios_internos]})
env.cr.commit()
```

---

## View Configuration

The default view mode for the `room.booking` action was changed to `gantt,calendar,form` to prioritize the Gantt view (which includes a **New** button) while keeping the calendar available.

If this needs to be reset, run in the shell:

```python
action = env['ir.actions.act_window'].search([('res_model', '=', 'room.booking')], limit=1)
action.view_mode = 'gantt,calendar,form'
env.cr.commit()
```

---

## Technical Notes

### `_compute_display_name` Override
The module overrides `_compute_display_name` on `room.booking`. This field is used by the Calendar view to render event titles. By returning `"Reservada"` for users without access, the privacy is enforced natively across all views without requiring view-level hacks.

### JavaScript Patches
Two JS patches are included in `static/src/`:

- **`room_booking_gantt_patch.js`** — Patches `GanttRenderer.prototype`:
  - `getDisplayName`: uses `display_name` (already controlled server-side)
  - `getPopoverProps`: sets `button = null` when `can_see_details === false`, removing the Edit button from the Gantt popover

- **`room_booking_calendar_patch.js`** — Patches `CalendarCommonPopover.prototype`:
  - `isEventEditable` getter: returns `false` when `can_see_details === false`, hiding the Edit button from the Calendar popover

### Admin Users Bypass Record Rules
Odoo administrators (`_is_admin() = True`) always bypass record rules by design. This is expected behavior — admins see and can edit everything regardless of group assignment.

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -c /etc/odoo/odoo.conf -i proyelec_salas --stop-after-init

# Update
odoo-update proyelec_salas
```

---

## File Structure

```
proyelec_salas/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── room_booking.py          # Model extension
├── security/
│   ├── proyelec_salas_groups.xml  # Group definitions
│   ├── ir.model.access.csv        # Access rights
│   └── record_rules.xml           # Write/delete restriction per user
├── views/
│   └── room_booking_views.xml     # View inheritance (form, calendar, gantt, kanban)
└── static/src/
    ├── room_booking_gantt_patch.js     # JS patch for Gantt popover
    └── room_booking_calendar_patch.js  # JS patch for Calendar popover
```

---

## Suggested Commit Messages

When pushing this module to the repository, use the following commit messages:

```
[ADD] proyelec_salas: meeting room privacy and attendee management

- Extend room.booking with is_private, attendee_ids, description fields
- Override _compute_display_name to show 'Reservada' for unauthorized users
- Add can_see_details computed field to control form field visibility
- Add internal notification on booking create/update for attendees
- Define Usuario and Lider/Gerencia security groups
- Add record rule: users can only edit/delete own bookings
- Patch GanttRenderer to hide Edit button for unauthorized users
- Patch CalendarCommonPopover to hide Edit button for unauthorized users
- Change default view mode to gantt,calendar,form
```

---

## Known Limitations

- The modal title (breadcrumb) when opening a booking via the Calendar popover may still show the real name before the form loads. This is a minor UX issue with no functional impact — the form itself hides all sensitive fields correctly.
- Admin users always bypass privacy rules. This is standard Odoo behavior.
- The `can_see_details` field is not stored — it is computed per request. This means it cannot be used in search filters or group-by operations.
