# proyelec_crm_celebrate — Won Opportunity Celebration

**Version:** 17.0.1.0.0  
**Author:** Juan David Villasmil — AIT Proyelec  
**License:** LGPL-3  
**Depends on:** `crm`, `mail`

---

## Overview

When a CRM opportunity is moved to a **Won** stage, this module automatically posts a celebration message to a configured Discuss channel. The message is sent by OdooBot and includes the opportunity name, customer, and deadline date. The native rainbow-man animation is suppressed in favour of the channel announcement.

---

## Features

- Detects transitions into any stage where `is_won = True`.
- Posts a structured HTML message to the target channel using OdooBot as the author.
- Errors during posting are caught and logged — they never block the user from marking the opportunity as won.
- The rainbow-man animation (`action_set_won_rainbowman`) is disabled to avoid UI noise.

### Message format

```
🏆 ¡OPORTUNIDAD GANADA!

<Opportunity name>
<Customer name>
<Deadline date>

¡Felicitaciones al equipo! 💪
```

---

## Configuration

The target channel is stored in a system parameter:

| Parameter key | Default | Description |
|---|---|---|
| `proyelec_crm_celebrate.channel_id` | `1` | Database ID of the `discuss.channel` to post to. |

To change the channel:

1. Go to **Settings → Technical → Parameters → System Parameters**.
2. Find the key `proyelec_crm_celebrate.channel_id`.
3. Set the value to the ID of your desired Discuss channel.

To find a channel's ID, open it in Discuss and check the URL (`/discuss/channel/<id>`), or inspect the record from the developer menu.

---

## File Structure

```
proyelec_crm_celebrate/
├── __manifest__.py
├── data/
│   └── ir_config_parameter.xml   # Sets default channel_id = 1
└── models/
    └── crm_lead.py                # write() hook + _post_celebrate_message()
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_crm_celebrate --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_crm_celebrate --stop-after-init
```

After installation, update the `proyelec_crm_celebrate.channel_id` system parameter to point to the correct channel.
