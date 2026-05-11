# E-Commerce Management System Documentation

This directory contains the technical and operational documentation for the Single Vendor E-Commerce Platform.

## Backend Planning

- [Backend Build Plan](./backend-plan.md) - Implementation roadmap, backend module boundaries, and engineering principles.
- [Final Database Design](./database-final.md) - Finalized backend data model with audit, payments, returns, coupons, and inventory details.
- [API V1 Contract](./api-v1-contract.md) - Versioned REST API endpoints, permissions, request bodies, responses, and error codes.

## Core Architecture And Setup

- [System Architecture](./01-ARCHITECTURE.md) - Tech stack, service design, and system architecture.
- [Project Setup And Standards](./11-PROJECT-SETUP.md) - Local installation, package management, and coding conventions.
- [Database Schema](./09-DATABASE.md) - Initial entity definitions and database notes.
- [Security Requirements](./10-SECURITY.md) - JWT authentication, RBAC, and API safety.

## Features And Workflows

- [System Workflows](./08-WORKFLOWS.md) - Checkout, inventory, payment, and return workflows.
- [User Roles And Permissions](./02-USER-ROLES.md) - Access control levels for Admin, Staff, and Customer.
- [Products And Inventory](./03-PRODUCTS-INVENTORY.md) - Product, variant, and stock integrity rules.
- [Orders And Checkout](./04-ORDERS-CHECKOUT.md) - Cart logic, order states, and edit policies.
- [Payments And Shipping](./05-PAYMENTS-SHIPPING.md) - Stripe integration, webhooks, and tracking.
- [Return Management](./06-RETURNS.md) - Return eligibility, approval workflows, and refunds.
- [Additional Features](./07-FEATURES.md) - Search, wishlist, reviews, notifications, admin, and analytics.

## Technology Summary

| Layer | Technology |
| --- | --- |
| Frontend | Next.js |
| Backend | Django REST Framework |
| Database | PostgreSQL |
| Payments | Stripe |
| Notifications | Email, Twilio |
| Testing | pytest |
| Code Quality | Ruff, Mypy |

Version: 1.0

Last updated: May 2026
