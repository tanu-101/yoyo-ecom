# 📘 E-Commerce Management System - Documentation

This directory contains the comprehensive technical and operational documentation for the Single Vendor E-Commerce Platform.

---

## 🏗 Core Architecture & Setup
- **[🏗 System Architecture](./01-ARCHITECTURE.md)** - Tech stack, service design, and Mermaid data flow diagrams.
- **[🏭 Project Setup & Standards](./11-PROJECT-SETUP.md)** - Local installation, `uv` commands, and coding conventions.
- **[🗄 Database Schema](./09-DATABASE.md)** - ERD diagram, entity definitions, and UUID standards.
- **[🛡 Security Requirements](./10-SECURITY.md)** - JWT authentication, RBAC permission matrix, and API safety.

---

## 🛒 Features & Workflows
- **[🔄 System Workflows](./08-WORKFLOWS.md)** - Sequence diagrams for Checkout, Inventory Locking, and Returns.
- **[👥 User Roles & Permissions](./02-USER-ROLES.md)** - Detailed access control levels (Admin, Staff, Customer).
- **[🛒 Products & Inventory](./03-PRODUCTS-INVENTORY.md)** - Product/Variant structure and stock integrity rules.
- **[🛍 Orders & Checkout](./04-ORDERS-CHECKOUT.md)** - Cart logic, order states, and edit policies.
- **[💳 Payments & Shipping](./05-PAYMENTS-SHIPPING.md)** - Stripe integration, webhooks, and tracking.
- **[🔁 Return Management](./06-RETURNS.md)** - Return eligibility, approval workflows, and refunds.
- **[✨ Additional Features](./07-FEATURES.md)** - Search optimization, Wishlist, and Reviews.

---

## 📋 Technology Summary

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js (TypeScript) |
| **Backend** | Django REST Framework |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Payments** | Stripe |
| **Testing** | pytest |

---

**Version:** 1.0  
**Last Updated:** May 2026
