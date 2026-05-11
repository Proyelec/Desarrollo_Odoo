# Proyelec - Procura KPI

**Version:** 17.0.1.0.0  
**Author:** Proyelec  
**License:** LGPL-3  
**Category:** Project

## Description

Adds an effectiveness KPI to project tasks in the PROCURA project, calculated as the ratio of won lines over total quoted lines. Displayed as a progress bar in the list view and as a badge in the kanban view.

## Features

- **KPI Effectiveness (%)** field on project tasks, shown as a progress bar in list view
- Visual badge in kanban view with the effectiveness percentage
- **"With Lines (PROCURA)"** filter to find tasks with KPI greater than 0 in the PROCURA project

## Installation

> ⚠️ This module requires the `x_kpi_efectividad` field to exist on `project.task` (created via Odoo Studio or a prior migration).

1. Copy the module into your Odoo addons directory
2. Update the module list
3. Install **Proyelec - Procura KPI**

## Dependencies

- `project`

## Status

Module is complete and functional. Pending deployment to production environment.
