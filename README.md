# 👑 AURA Luxury Gold Jewellery E-Commerce Shopping Platform

A modern, commercial-grade, responsive Gold & Diamond Jewellery E-Commerce Web Application crafted with Python Django, MySQL, Bootstrap 5, and JavaScript. Featuring a regal luxury jewellery aesthetic, interactive 360-degree multi-angle product rotation viewer, high-resolution magnifying hover zoom, customer authentication, shopping cart, GST-compliant checkout, live order tracking, printable tax invoices, and a dedicated Bespoke Custom Jewellery Design Studio with multiple reference image uploads.

---

## 🌟 Key Highlights & Feature Matrix

### 1. 💎 Premium Luxury UI/UX Design
- **Regal Palette**: Royal Gold (`#D4AF37`), Antique Champagne (`#B8860B`), Obsidian Midnight (`#0D0D0D`), Ivory Cream (`#FAF8F5`), and Silk White (`#FFFFFF`).
- **Typography**: Serif titles in `Cinzel` & `Playfair Display`, clean body in `Montserrat`.
- **Live Daily Gold Rate Ticker**: Real-time ticker bar on top displaying live 24K, 22K, 18K gold and silver rates per gram.
- **BIS 916 Hallmark Assurance**: Laser HUID authenticity guarantees across all pieces.
- **Responsive Layout**: Optimized for desktop, tablet, and mobile screens.

### 2. 🔄 Interactive 360-Degree Product Rotation Viewer
- **True Multi-Angle Image Frames**: Driven by 24 actual sequential angle frames (0° to 345° in 15° increments) captured around the jewellery piece.
- **Mouse Drag & Touch Swipe**: Smooth drag rotation on desktop and swipe gestures on mobile devices.
- **Autoplay 360 Mode**: Play/Pause automatic continuous rotation.
- **Scrubber Slider**: Real-time degree calculation and frame counter (e.g., `180° (12/24)`).
- **Zoom & Fullscreen**: Zoom in (+), zoom out (-), reset view, and native fullscreen mode.
- **Admin 360 Management**: Administrators can upload sequences of multi-angle frames directly for any product.

### 3. 🔍 High-Resolution Image Zoom & Gallery
- **Magnifying Hover Lens**: Smooth lens magnification on desktop.
- **Click-to-Fullscreen Lightbox**: Full-resolution modal viewer for intricate gemstone examination.
- **Thumbnail Navigation**: Instant gallery switching with active golden ring indicator.

### 4. 🎨 Bespoke Custom Jewellery Design Studio
- **Dedicated Module** at `/custom-jewellery/`.
- **Customization Request Form**:
  - Customer contact details (Name, Email, Mobile).
  - Jewellery Type (Ring, Necklace, Pendant, Bangle, Earrings, Bracelet, Bridal Set).
  - Metal Type (Yellow Gold, Rose Gold, White Gold, Platinum, Silver) & Gold Purity (24K, 22K, 18K, 14K).
  - Expected Weight (Grams) & Preferred Budget (₹ INR).
  - Ring size and necklace length sizing.
  - Detailed design vision & special engraving instructions.
- **Multiple Reference Image Upload**:
  - Drag-and-drop file upload zone.
  - Supports JPG, JPEG, PNG, WEBP design sketches, photos, and 3D CAD renders.
  - Instant client-side preview thumbnails with remove button.
- **Artisan Quotation & Pipeline**:
  - Status lifecycle: `Pending` → `Under Review` → `3D CAD Design` → `Quotation Sent` → `Approved` → `In Production` → `Ready for Delivery` → `Delivered`.
  - Admin Quotation Builder: estimates metal weight, metal rate applied, making charges, stone charges, GST (3%), total estimated price, and 3D CAD blueprint file.
  - Customer can review the quote and choose to **Accept Quotation** or **Request Revision** directly from their tracker!

### 5. 🛍️ Shopping Cart & Price Transparency
- Supports guest session carts with automatic seamless synchronization upon customer login.
- Real-time subtotal, craftsmanship making charges, and Indian Jewellery GST (3%) calculations.
- Live AJAX add-to-cart toast notifications and sliding offcanvas quick-cart drawer.

### 6. 💳 Checkout, Payments & Order Management
- **Multi-Step Checkout**:
  - Customer contact details.
  - Saved address book selection or instant new address creation.
  - Billing address toggle.
  - Payment Methods:
    - **UPI / Instant QR Code** (Interactive simulated QR code payment verification).
    - **Credit / Debit Card & NetBanking** (Simulated gateway).
    - **Insured Cash on Delivery (COD)**.
    - **Direct Showroom Bank Transfer / RTGS**.
- **Unique Order Number Generation**: e.g., `GJ-202611-9281`.
- **Real-Time Order Tracking**: Visual milestone tracker (Confirmed → Hallmarking & Crafting → Dispatched → Out for Delivery → Delivered).
- **Printable GST-Compliant Tax Invoice**: Formatted with company GSTIN `29AABCJ8492K1Z9`, HSN Code `7113`, CGST (1.5%), SGST (1.5%), breakdown of net gold weight, making charges, and authorized signature.
- **Customer Cancellation**: Self-service cancellation if order is in Pending or Confirmed status.

### 7. 🔒 Complete User Authentication & Account Center
- User Registration with validation.
- User Login & Logout with session management.
- Forgot Password request & reset flow.
- Customer Profile Management with avatar photo upload and loyalty points.
- Address Book (Multiple addresses: Shipping, Billing, Home, Office with default selector).
- Saved Wishlist with one-click "Move to Bag" or remove.
- Order History with quick invoice and tracking links.

### 8. 📊 Executive Admin Dashboard & Inventory CRUD
- **Executive KPI Cards**: Total Revenue, Total Orders, Total Products, Custom Requests, Pending Confirmations.
- **Interactive Analytics**: Inventory distribution donut chart powered by Chart.js.
- **Complete Product CRUD**:
  - Create, view, edit, and delete products.
  - Filter by Category, Metal Type, Purity, Availability, and Search query.
  - Manage multiple gallery images and sequential 360° frames.
- **Category & Taxonomy CRUD**: Manage categories, display orders, and icon styling.
- **Customer CRM Directory**: View all patrons, order count, total lifetime spend, and toggle account active/suspended status.

---

## 🏗️ Technology Stack

| Component | Technology |
|---|---|
| **Backend Framework** | Python 3.7+ / Django 3.2+ |
| **Database** | MySQL (with PyMySQL driver) + automatic SQLite fallback |
| **Image Processing** | Pillow (PIL 9.5+) |
| **REST API** | Django REST Framework (DRF 3.15+) |
| **Frontend Framework**| HTML5, CSS3, Bootstrap 5.3 |
| **Icons & Typography**| Bootstrap Icons 1.11, Google Fonts (*Cinzel*, *Playfair Display*, *Montserrat*) |
| **360° Viewer** | Vanilla JavaScript Multi-Angle 360° Sequence Viewer |
| **Image Zoom** | Vanilla JavaScript Lens Magnifier & Lightbox Modal |

---

## 📁 Project Directory Structure

```text
Jewellery_Shop/
│── manage.py                          # Django management CLI
│── run.bat                            # Windows 1-click launcher batch script
│── run.ps1                            # Windows PowerShell launcher script
│── generate_sample_assets.py          # Pillow media & database seeder script
│── verify_all_endpoints.py            # Comprehensive 25+ view verification script
│── .env                               # Database & Django environment configuration
│
├── jewellery_shop/                    # Project Configuration
│   ├── settings.py                    # Master settings (MySQL / SQLite fallback, apps, gold rates)
│   ├── urls.py                        # Root URL routing
│   ├── wsgi.py & asgi.py              # WSGI & ASGI servers
│
├── core/                              # Homepage, About, Contact & Global Processors
│   ├── models.py                      # HeroBanner, Testimonial, Subscriber, ContactInquiry
│   ├── context_processors.py          # Global gold rates, cart count, wishlist count
│   ├── views.py & urls.py             # Home, About, Contact, Newsletter
│   └── tests.py                       # Core test suite
│
├── accounts/                          # Authentication, Profiles & Wishlist
│   ├── models.py                      # UserProfile, Address, Wishlist, WishlistItem, Notification
│   ├── forms.py                       # Registration, Login, Profile, Address forms
│   └── views.py & urls.py             # Auth views, Profile, Addresses, Wishlist API
│
├── products/                          # Product Catalog, CRUD, 360 Viewer
│   ├── models.py                      # Category, SubCategory, Product, ProductImage, Product360Image, Review
│   ├── forms.py                       # ProductForm, CategoryForm, ReviewForm
│   └── views.py & urls.py             # Catalog list, detail, 360 viewer, admin CRUD
│
├── cart/                              # Shopping Bag & GST Calculation
│   ├── models.py                      # Cart, CartItem
│   └── views.py & urls.py             # Cart detail, add, update, remove, quick drawer
│
├── orders/                            # Checkout, Fulfillment, Invoices & Tracking
│   ├── models.py                      # Order, OrderItem, Payment
│   └── views.py & urls.py             # Checkout, confirmation, history, tracking, tax invoice
│
├── custom_orders/                     # Bespoke Custom Jewellery Design Studio
│   ├── models.py                      # CustomOrder, CustomOrderImage, CustomOrderQuotation
│   ├── forms.py                       # CustomOrderRequestForm, QuotationForm
│   └── views.py & urls.py             # Request form, image uploads, quotation workflow
│
├── admin_portal/                      # Executive Admin Dashboard & CRM
│   └── views.py & urls.py             # KPI analytics, order fulfillment, customer CRM
│
├── api/                               # Django REST Framework Endpoints
│   ├── serializers.py                 # DRF Serializers for Products, 360 frames, Cart
│   ├── views.py & urls.py             # API endpoints
│   └── tests.py                       # API test suite
│
├── templates/                         # HTML5 Django Templates
│   ├── base.html                      # Master luxury base template
│   ├── includes/                      # Navbar, Footer, Messages, Cart Drawer
│   ├── core/                          # home.html, about.html, contact.html
│   ├── accounts/                      # login, register, profile, addresses, wishlist
│   ├── products/                      # product_list, product_detail, admin CRUD templates
│   ├── cart/                          # cart_detail.html
│   ├── orders/                        # checkout.html, confirmation, tracking, invoice.html
│   ├── custom_orders/                 # custom_request_form, custom_order_detail
│   └── admin_portal/                  # dashboard, orders_list, customers_list
│
├── static/                            # Static Assets
│   ├── css/luxury-theme.css           # Master custom luxury gold CSS styling
│   ├── js/viewer-360.js               # 360° interactive rotation viewer engine
│   ├── js/image-zoom.js               # Lens hover magnifier & lightbox gallery
│   └── js/main.js                     # AJAX cart, wishlist heart toggle, pincode check
│
└── media/                             # Dynamic Uploads
    ├── products/gallery/              # High-resolution product images
    ├── products/360/                  # True 24-frame multi-angle sequence images
    ├── banners/                       # Collection hero banners
    └── custom_orders/                 # Customer reference photos & 3D CAD blueprints
```

---

## 🚀 Quick Start Guide

### 1. Launching with Launcher Scripts
Simply double-click `run.bat` or run:
```powershell
.\run.ps1
```

### 2. Manual Command-Line Startup
Run the development server using Python:
```bash
python manage.py runserver 127.0.0.1:8000
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo User Credentials

| Role | Username | Password | Access Capabilities |
|---|---|---|---|
| **Super Admin** | `admin` | `Admin@123` | Full access to Admin Dashboard, Product CRUD, 360 Upload, Order Fulfillment, Quotation Builder, Customer CRM |
| **Customer** | `customer` | `Customer@123` | Customer Profile, Wishlist, Shopping Bag, Checkout, Order Tracking, Custom Design Studio |

*(You can also register any new customer account directly from the Sign In / Register page!)*

---

## 🗄️ MySQL Database Setup & Configuration

The application is engineered to connect to **MySQL** using `PyMySQL`. In `jewellery_shop/settings.py`, database settings are configured via environment variables or the `.env` file:

```ini
# .env file configuration
DB_ENGINE=mysql
DB_NAME=jewellery_shop_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

> **Automatic Graceful Fallback**: If your local MySQL service is offline or credentials are not yet entered, the application automatically uses SQLite (`db.sqlite3`) so the platform runs immediately without disruption! When you provide your MySQL credentials, it will automatically connect to MySQL and create the `jewellery_shop_db` database with all normalized tables.

---

## 🧪 Testing and Verification

Run the automated test suite anytime:
```bash
# Run unit tests
python manage.py test core
python manage.py test api

# Run comprehensive endpoint verification across all 25+ routes
python verify_all_endpoints.py
```
All unit tests and endpoint health checks pass with **HTTP 200 OK**.

