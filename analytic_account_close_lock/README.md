# Analytic Account Close Lock

**Version:** 17.0.1.0.0  
**Author:** Juan Villasmil  
**License:** LGPL-3  
**Category:** Accounting

## Description

Allows closing analytic accounts to block new postings on them. Once an account is closed, no analytic lines or journal entries referencing it can be created or modified.

## Features

- **"Closed for posting"** boolean field on each analytic account
- Automatic recording of the **closing date** and the **user** who closed it
- Access restriction: only users in the **Analytic Close Manager** group can open or close accounts
- When reopening an account, the closing date and user are automatically cleared

## Installation

1. Copy the module into your Odoo addons directory
2. Update the module list
3. Install **Analytic Account Close Lock**
4. Assign the **Analytic Close Manager** group to authorized users

## Dependencies

- `account`
- `analytic`

## Usage

1. Go to **Accounting → Analytic → Analytic Accounts**
2. Open the account you want to close
3. Check the **"Closed for posting"** field
4. From that point on, any attempt to post entries to that account will be blocked
