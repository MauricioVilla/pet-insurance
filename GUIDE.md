# 📘 Application Guide — Pet Insurance Reimbursement Platform

This document explains how the application works from the perspective of each user role.

---

## Table of Contents

- [Overview](#overview)
- [User Roles](#user-roles)
- [Customer Guide](#customer-guide)
- [Support Guide](#support-guide)
- [Admin Guide](#admin-guide)
- [Pet Statuses](#pet-statuses)
- [Claim Statuses](#claim-statuses)

---

## Overview

The Pet Insurance Reimbursement Platform allows customers to register their pets, get insurance coverage approved by support staff, and submit reimbursement claims for veterinary expenses. Support and admin users review and process those claims.

---

## User Roles

| Role | Description |
|---|---|
| **Customer** | Pet owner. Registers pets, submits reimbursement claims, and tracks their status. |
| **Support** | Insurance staff. Reviews pets for coverage approval and approves/rejects claims. |
| **Admin** | Full access. Same capabilities as Support plus access to the Django admin panel. |

---

## Customer Guide

### 1. Registration & Login

- Register with email, name, and password at the **Register** page.
- New accounts are assigned the **Customer** role by default.
- Log in with email and password to access the platform.

### 2. Registering a Pet

- Navigate to **My Pets**.
- Click **+ Add Pet** and fill in:
  - **Name** — pet's name.
  - **Species** — Dog, Cat, or Other.
  - **Birth Date** — date of birth.
- The pet is created with status **Pending**. It is not yet covered.
- You can **edit** or **delete** your pets while they are in Pending status.

### 3. Waiting for Coverage Approval

- A Support or Admin user must approve your pet and assign a coverage start date.
- Once approved:
  - If the coverage start date is **today or in the past** → pet status becomes **Active** immediately.
  - If the coverage start date is **in the future** → pet status becomes **Approved**, and it will automatically transition to **Active** when the date arrives.
- Coverage lasts **365 days** from the start date.

### 4. Submitting a Claim

- Navigate to **Claims** and click **+ New Claim**.
- Fill in the claim form:
  - **Pet** — select one of your pets (must have Active coverage).
  - **Invoice File** — upload the invoice (PDF, JPG, or PNG).
  - **Invoice Date** — must fall within the pet's coverage period.
  - **Date of Event** — the date of the veterinary visit.
  - **Amount** — the reimbursement amount requested.
- The claim is created with status **Processing**.

### 5. Claim Processing

- A background task automatically validates the claim:
  - If the **date of event** falls within the coverage period → status moves to **In Review**.
  - If not → status becomes **Rejected** with an explanation in the notes.
- Duplicate invoices (same file content) are rejected immediately.

### 6. Tracking Claims

- The **Claims** page shows all your claims with status tabs: All, Submitted, Processing, In Review, Approved, Rejected.
- You can view invoice files and review notes for each claim.

---

## Support Guide

### 1. Managing Pets

- Navigate to **Pets** to see **all** registered pets from all customers.
- For pets in **Pending** status, click **Approve** to assign a coverage start date.
  - A date picker modal appears. Select the coverage start date and confirm.
  - The pet transitions to **Approved** (future date) or **Active** (today or past).

### 2. Reviewing Claims

- Navigate to **Claims** to see **all** claims from all customers.
- Use the status tabs to filter (e.g., show only **In Review** claims).
- For claims in **In Review** status:
  - Click **✓ Approve** to approve the reimbursement. Optionally add notes.
  - Click **✗ Reject** to reject the claim. Optionally add notes explaining why.
- You can view invoice files by clicking **📄 View** on any claim.
- The **Owner** column shows the customer's name and email for reference.

---

## Admin Guide

Admin users have all the capabilities of Support, plus:

- **Django Admin Panel** — accessible at `/admin/` for direct database management.
- Full CRUD access to all users, pets, and claims through the admin interface.

---

## Pet Statuses

```
PENDING ──→ APPROVED ──→ ACTIVE
              (future)     (coverage_start ≤ today)
```

| Status | Description |
|---|---|
| **Pending** | Pet registered by customer, awaiting coverage approval from support. |
| **Approved** | Coverage approved with a future start date. Will auto-activate when the date arrives. |
| **Active** | Coverage is active. Claims can be submitted for this pet. Coverage lasts 365 days. |

The transition from **Approved** → **Active** happens automatically via a daily scheduled task (Celery Beat, runs at 00:05).

---

## Claim Statuses

```
PROCESSING ──→ IN_REVIEW ──→ APPROVED
                    │
                    └──→ REJECTED
```

| Status | Description |
|---|---|
| **Processing** | Claim submitted. Background task is validating invoice and coverage dates. |
| **In Review** | Validation passed. Waiting for Support/Admin to approve or reject. |
| **Approved** | Claim approved by Support/Admin. Reimbursement will be processed. |
| **Rejected** | Claim rejected (either automatically by validation or manually by Support/Admin). Review notes explain the reason. |

---

## Business Rules Summary

| Rule | Detail |
|---|---|
| Coverage duration | 365 days from `coverage_start` |
| Invoice date | Must fall within the pet's coverage period |
| Date of event | Validated by Celery task; must be within coverage |
| Duplicate invoices | Detected via SHA-256 hash of the file; rejected immediately |
| Pet must be Active | Only pets with Active coverage can have claims submitted |
