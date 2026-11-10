import os
import sys
import math
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewellery_shop.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.core.files import File
from core.models import Subscriber, Testimonial, ContactInquiry, HeroBanner
from accounts.models import UserProfile, Address, Wishlist
from products.models import Category, SubCategory, Product, ProductImage, Product360Image, Review
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem, Payment
from custom_orders.models import CustomOrder, CustomOrderImage, CustomOrderQuotation

# Helper to draw gold gradients and jewelry
def draw_gradient_background(draw, width, height, top_color, bottom_color):
    for y in range(height):
        ratio = y / float(height)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def create_jewellery_card_image(title, subtitle, item_type, width=800, height=800, angle=0):
    img = Image.new('RGB', (width, height), (250, 248, 245))
    draw = ImageDraw.Draw(img)
    
    # Warm luxury gradient
    draw_gradient_background(draw, width, height, (253, 251, 247), (242, 236, 226))
    
    # Elegant inner border with gold accents
    border_margin = 35
    draw.rectangle(
        [(border_margin, border_margin), (width - border_margin, height - border_margin)],
        outline=(212, 175, 55), width=2
    )
    draw.rectangle(
        [(border_margin + 6, border_margin + 6), (width - border_margin - 6, height - border_margin - 6)],
        outline=(230, 210, 150), width=1
    )
    
    # Corner ornaments
    orn_size = 20
    for cx, cy in [
        (border_margin, border_margin),
        (width - border_margin, border_margin),
        (border_margin, height - border_margin),
        (width - border_margin, height - border_margin)
    ]:
        draw.polygon([(cx - orn_size, cy), (cx, cy - orn_size), (cx + orn_size, cy), (cx, cy + orn_size)], fill=(212, 175, 55))

    cx, cy = width // 2, height // 2 - 20
    
    # Draw jewellery based on item_type and angle (for 360 degree rotation)
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    # Cast shadow
    shadow_w = int(220 * abs(cos_a) + 140 * abs(sin_a))
    draw.ellipse(
        [(cx - shadow_w // 2, cy + 190), (cx + shadow_w // 2, cy + 225)],
        fill=(220, 215, 205)
    )

    if item_type == 'ring':
        # Ring rotation in 3D: elliptical projection
        ring_r = 130
        band_thickness = 22
        rx = int(ring_r * (0.35 + 0.65 * abs(cos_a)))
        ry = int(ring_r * 0.95)
        
        # Gold band outer
        draw.ellipse([(cx - rx, cy - ry), (cx + rx, cy + ry)], outline=(197, 160, 89), width=band_thickness)
        draw.ellipse([(cx - rx + 4, cy - ry + 4), (cx + rx - 4, cy + ry - 4)], outline=(245, 215, 127), width=4)
        
        # Solitaire diamond prong mount at top, rotating with angle
        mount_x = cx + int(sin_a * 80)
        mount_y = cy - ry + int(abs(sin_a) * 30)
        
        # Diamond prongs
        for dx, dy in [(-16, 5), (16, 5), (-14, -18), (14, -18)]:
            draw.line([(mount_x, mount_y), (mount_x + dx, mount_y + dy)], fill=(210, 210, 210), width=4)
        
        # Sparkling Brilliant Diamond
        d_size = 38
        diamond_pts = [
            (mount_x, mount_y - d_size),
            (mount_x + int(d_size * 0.85), mount_y - int(d_size * 0.4)),
            (mount_x + int(d_size * 0.55), mount_y + int(d_size * 0.6)),
            (mount_x - int(d_size * 0.55), mount_y + int(d_size * 0.6)),
            (mount_x - int(d_size * 0.85), mount_y - int(d_size * 0.4)),
        ]
        draw.polygon(diamond_pts, fill=(240, 248, 255), outline=(180, 210, 235))
        # Inner facets
        draw.line([(mount_x, mount_y - d_size), (mount_x, mount_y + int(d_size * 0.6))], fill=(255, 255, 255), width=2)
        draw.line([(diamond_pts[1][0], diamond_pts[1][1]), (diamond_pts[4][0], diamond_pts[4][1])], fill=(225, 240, 255), width=2)
        # Gem sparkle
        draw.line([(mount_x - 12, mount_y - 12), (mount_x + 12, mount_y - 12)], fill=(255, 255, 255), width=3)
        draw.line([(mount_x, mount_y - 24), (mount_x, mount_y)], fill=(255, 255, 255), width=3)

    elif item_type == 'necklace':
        # Royal Kundan necklace collar arc
        arc_w = int(240 * (0.8 + 0.2 * abs(cos_a)))
        arc_h = 220
        # Draw multi-strand gold chain
        for r_offset in [0, 16, 32]:
            draw.arc(
                [(cx - arc_w - r_offset, cy - arc_h), (cx + arc_w + r_offset, cy + arc_h)],
                start=20, end=160, fill=(212, 175, 55), width=6
            )
        # Gemstone pendants hanging along necklace arc
        pendant_count = 11
        for i in range(pendant_count):
            theta = math.radians(35 + (i * 110 / (pendant_count - 1)) + (sin_a * 8))
            px = cx + int(math.cos(theta) * (arc_w + 35))
            py = cy + int(math.sin(theta) * (arc_h - 10))
            # Gold bezel
            draw.ellipse([(px - 14, py - 14), (px + 14, py + 14)], fill=(212, 175, 55))
            # Alternating Ruby & Emerald centers
            gem_color = (175, 25, 45) if i % 2 == 0 else (20, 120, 60)
            draw.ellipse([(px - 9, py - 9), (px + 9, py + 9)], fill=gem_color)
            # Pearl drop
            draw.ellipse([(px - 6, py + 16), (px + 6, py + 30)], fill=(250, 248, 240), outline=(210, 180, 90))

        # Center Royal Pendant
        center_px = cx + int(sin_a * 35)
        center_py = cy + arc_h - 20
        draw.polygon([
            (center_px, center_py + 65),
            (center_px - 38, center_py + 20),
            (center_px - 25, center_py - 15),
            (center_px + 25, center_py - 15),
            (center_px + 38, center_py + 20)
        ], fill=(212, 175, 55), outline=(180, 140, 30))
        draw.ellipse([(center_px - 16, center_py + 10), (center_px + 16, center_py + 42)], fill=(175, 25, 45))
        draw.ellipse([(center_px - 8, center_py + 75), (center_px + 8, center_py + 95)], fill=(255, 255, 250), outline=(200, 170, 70))

    elif item_type == 'earrings':
        # Jhumkas pair
        for side in [-1, 1]:
            ex = cx + (side * 110) + int(sin_a * side * 20)
            ey = cy - 40
            # Stud flower
            draw.ellipse([(ex - 22, ey - 22), (ex + 22, ey + 22)], fill=(212, 175, 55))
            draw.ellipse([(ex - 10, ey - 10), (ex + 10, ey + 10)], fill=(175, 25, 45))
            # Hanging connector
            draw.line([(ex, ey + 22), (ex, ey + 50)], fill=(190, 150, 40), width=4)
            # Dome / Jhumka bell
            dome_w = 48
            dome_h = 36
            draw.chord([(ex - dome_w, ey + 45), (ex + dome_w, ey + 45 + dome_h * 2)], start=180, end=360, fill=(225, 185, 65), outline=(180, 140, 30))
            # Hanging mini pearls
            for p in range(-4, 5):
                mpx = ex + p * 10
                mpy = ey + 50 + dome_h
                draw.ellipse([(mpx - 4, mpy), (mpx + 4, mpy + 10)], fill=(250, 248, 242), outline=(190, 160, 60))

    elif item_type == 'bangles':
        # Royal kada / bangle
        b_rx = int(170 * (0.6 + 0.4 * abs(cos_a)))
        b_ry = 130
        for off in [-30, 0, 30]:
            draw.ellipse([(cx - b_rx, cy - b_ry + off), (cx + b_rx, cy + b_ry + off)], outline=(212, 175, 55), width=18)
            draw.ellipse([(cx - b_rx + 2, cy - b_ry + off + 2), (cx + b_rx - 2, cy + b_ry + off - 2)], outline=(255, 225, 120), width=4)
            # Studded floral embossing
            for k in range(8):
                ang_k = math.radians(k * 45 + angle)
                kx = cx + int(math.cos(ang_k) * (b_rx - 8))
                ky = cy + int(math.sin(ang_k) * (b_ry - 8)) + off
                draw.ellipse([(kx - 6, ky - 6), (kx + 6, ky + 6)], fill=(185, 30, 45) if k % 2 == 0 else (240, 245, 255))

    elif item_type == 'coin':
        # 24K Sovereign Bullion Coin
        coin_rx = int(140 * (0.4 + 0.6 * abs(cos_a)))
        coin_ry = 140
        draw.ellipse([(cx - coin_rx, cy - coin_ry), (cx + coin_rx, cy + coin_ry)], fill=(228, 185, 45), outline=(175, 130, 20), width=6)
        draw.ellipse([(cx - coin_rx + 14, cy - coin_ry + 14), (cx + coin_rx - 14, cy + coin_ry - 14)], outline=(255, 225, 110), width=3)
        # Engraved 24K 999 Hallmark text / symbol
        draw.ellipse([(cx - 45, cy - 45), (cx + 45, cy + 45)], outline=(190, 150, 30), width=2)
        # Star motif
        for s in range(8):
            ang_s = math.radians(s * 45)
            draw.line([(cx, cy), (cx + int(math.cos(ang_s) * 35), cy + int(math.sin(ang_s) * 35))], fill=(255, 235, 140), width=2)

    # Hallmarking Ribbon Badge on image
    draw.rectangle([(width - 240, 50), (width - 50, 95)], fill=(17, 17, 17))
    draw.rectangle([(width - 238, 52), (width - 52, 93)], outline=(212, 175, 55), width=1)
    
    # Text overlay at bottom
    text_bg_y = height - 120
    draw.rectangle([(50, text_bg_y), (width - 50, height - 50)], fill=(17, 17, 17, 230))
    draw.rectangle([(52, text_bg_y + 2), (width - 52, height - 52)], outline=(212, 175, 55), width=1)
    
    return img

def main():
    print("=" * 60)
    print("AURA LUXURY JEWELLERY - SEEDING DATABASE & SAMPLE MEDIA")
    print("=" * 60)
    
    # 1. Create Superuser and Normal Customer
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@aurajewels.com',
        'first_name': 'Victoria',
        'last_name': 'Royale',
        'is_staff': True,
        'is_superuser': True,
    })
    admin_user.set_password('Admin@123')
    admin_user.save()
    if created:
        print("[✓] Superuser 'admin' created (Password: Admin@123)")
    else:
        print("[✓] Superuser 'admin' updated (Password: Admin@123)")

    customer_user, c_created = User.objects.get_or_create(username='customer', defaults={
        'email': 'customer@gmail.com',
        'first_name': 'Ananya',
        'last_name': 'Sharma',
    })
    customer_user.set_password('Customer@123')
    customer_user.save()
    if c_created:
        print("[✓] Customer user 'customer' created (Password: Customer@123)")

    # Ensure profile and address
    profile = customer_user.profile
    profile.phone = "+91 98765 43210"
    profile.loyalty_points = 350
    profile.save()

    Address.objects.get_or_create(
        user=customer_user,
        address_type='SHIPPING',
        defaults={
            'full_name': 'Ananya Sharma',
            'phone': '+91 98765 43210',
            'street_address': 'Flat 402, Royale Heritage Palms, MG Road',
            'landmark': 'Opposite Taj Vivanta',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560001',
            'is_default': True,
        }
    )

    # 2. Categories & Subcategories
    categories_data = [
        {
            'name': 'Gold Jewellery',
            'slug': 'gold-jewellery',
            'description': 'Pure 22K & 24K BIS hallmarked gold masterfully crafted into exquisite heirlooms.',
            'icon_class': 'bi-gem',
            'is_featured': True,
            'display_order': 1,
            'subcategories': ['Necklaces', 'Rings', 'Earrings', 'Bangles', 'Chains']
        },
        {
            'name': 'Diamond Solitaires',
            'slug': 'diamond-solitaires',
            'description': 'Certified VVS-EF brilliant cut solitaire diamonds set in 18K white, rose, and yellow gold.',
            'icon_class': 'bi-suit-diamond',
            'is_featured': True,
            'display_order': 2,
            'subcategories': ['Engagement Rings', 'Solitaire Pendants', 'Tennis Bracelets', 'Diamond Studs']
        },
        {
            'name': 'Bridal Trousseau',
            'slug': 'bridal-trousseau',
            'description': 'Magnificent Kundan, Polki, and Temple wedding sets for royal brides.',
            'icon_class': 'bi-stars',
            'is_featured': True,
            'display_order': 3,
            'subcategories': ['Bridal Chokers', 'Matha Patti & Maang Tikka', 'Haath Phool', 'Kada & Bangles']
        },
        {
            'name': 'Antique & Temple',
            'slug': 'antique-temple',
            'description': 'Intricately handcrafted South Indian heritage temple jewellery with sacred motifs.',
            'icon_class': 'bi-flower1',
            'is_featured': True,
            'display_order': 4,
            'subcategories': ['Lakshmi Harams', 'Peacock Jhumkas', 'Coin Necklaces', 'Temple Vaddanam']
        },
        {
            'name': 'Daily Wear & Platinum',
            'slug': 'daily-wear-platinum',
            'description': 'Minimalist luxury, sleek 14K gold, and eternal 950 platinum for modern everyday elegance.',
            'icon_class': 'bi-brightness-high',
            'is_featured': False,
            'display_order': 5,
            'subcategories': ['Office Wear Pendants', 'Stackable Bands', 'Sleek Bracelets', 'Platinum Bands']
        },
        {
            'name': 'Gold Coins & Bullion',
            'slug': 'gold-coins-bullion',
            'description': '24K 999 purest gold coins and bars with tamper-proof certicard packaging.',
            'icon_class': 'bi-coin',
            'is_featured': False,
            'display_order': 6,
            'subcategories': ['5g Gold Coins', '10g Sovereign Coins', '20g Bullion Bars', 'Lakshmi Silver Coins']
        },
    ]

    cat_map = {}
    subcat_map = {}
    for c_data in categories_data:
        sub_list = c_data.pop('subcategories')
        cat, _ = Category.objects.get_or_create(slug=c_data['slug'], defaults=c_data)
        cat_map[cat.slug] = cat
        for s_name in sub_list:
            sub, _ = SubCategory.objects.get_or_create(category=cat, name=s_name)
            subcat_map[f"{cat.slug}_{s_name}"] = sub
    print(f"[✓] Created {len(cat_map)} Categories and subcategories.")

    # 3. Products List with Specifications
    products_data = [
        {
            'name': 'Royal Maharani 22K Kundan Choker Necklace',
            'sku': 'NK-GLD-916-001',
            'category_slug': 'bridal-trousseau',
            'subcategory_key': 'bridal-trousseau_Bridal Chokers',
            'metal_type': 'GOLD',
            'purity': '22K',
            'gross_weight': Decimal('48.650'),
            'net_weight': Decimal('42.100'),
            'stone_weight': Decimal('6.550'),
            'making_charges': Decimal('14500.00'),
            'base_price': Decimal('342000.00'),
            'discount_percent': Decimal('8.00'),
            'stock': 3,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': True,
            'is_trending': True,
            'is_bestseller': True,
            'is_new': True,
            'gender': 'WOMEN',
            'type_key': 'necklace',
            'description': 'Breathtaking bridal necklace handcrafted by Jaipur master artisans. Features uncut Polki stones encrusted in 22K hallmarked gold with natural Zambian emerald drops and south sea pearl tassels.',
            'specifications': 'BIS Hallmarked 916. Length: 16 inches with adjustable gold dori. Certificate: IGI Authenticated. Lock: Traditional royal screw clasp.',
        },
        {
            'name': 'Eternal Brilliance 1.5ct Solitaire Diamond Ring',
            'sku': 'RG-DIA-750-002',
            'category_slug': 'diamond-solitaires',
            'subcategory_key': 'diamond-solitaires_Engagement Rings',
            'metal_type': 'DIAMOND',
            'purity': '18K',
            'gross_weight': Decimal('6.200'),
            'net_weight': Decimal('5.900'),
            'stone_weight': Decimal('1.500'),
            'making_charges': Decimal('8500.00'),
            'base_price': Decimal('185000.00'),
            'discount_percent': Decimal('10.00'),
            'stock': 5,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': True,
            'is_trending': True,
            'is_bestseller': True,
            'is_new': False,
            'gender': 'WOMEN',
            'type_key': 'ring',
            'description': 'A timeless solitaire engagement ring featuring a GIA certified 1.50-carat round brilliant cut diamond of VVS1 clarity and E colorless grade, mounted on an 18K white gold cathedral band.',
            'specifications': 'Metal: 18K White Gold (Hallmarked 750). Diamond: 1.50 Ct, Triple Excellent Cut. Setting: 6-prong platinum claw mount. Ring Size: Indian 14 (resizing available).',
        },
        {
            'name': 'Imperial Peacock 22K Gold Antique Jhumkas',
            'sku': 'ER-GLD-916-003',
            'category_slug': 'antique-temple',
            'subcategory_key': 'antique-temple_Peacock Jhumkas',
            'metal_type': 'GOLD',
            'purity': '22K',
            'gross_weight': Decimal('24.800'),
            'net_weight': Decimal('22.400'),
            'stone_weight': Decimal('2.400'),
            'making_charges': Decimal('6800.00'),
            'base_price': Decimal('178000.00'),
            'discount_percent': Decimal('5.00'),
            'stock': 4,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': True,
            'is_trending': True,
            'is_bestseller': False,
            'is_new': True,
            'gender': 'WOMEN',
            'type_key': 'earrings',
            'description': 'Regal temple earrings showcasing dancing peacock motifs, intricate filigree domes, and hanging natural Basra pearl drops with vibrant Burmese ruby cabochons.',
            'specifications': 'Gold: 22K Yellow Antique Finish. Length: 55mm. Width: 26mm. Weight: 24.80g. Lock: South Indian Bombay screw closure.',
        },
        {
            'name': 'Heritage Lakshmi Antique 22K Gold Kada',
            'sku': 'BG-GLD-916-004',
            'category_slug': 'gold-jewellery',
            'subcategory_key': 'gold-jewellery_Bangles',
            'metal_type': 'GOLD',
            'purity': '22K',
            'gross_weight': Decimal('38.250'),
            'net_weight': Decimal('36.800'),
            'stone_weight': Decimal('1.450'),
            'making_charges': Decimal('11200.00'),
            'base_price': Decimal('275000.00'),
            'discount_percent': Decimal('0.00'),
            'stock': 2,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': True,
            'is_trending': False,
            'is_bestseller': True,
            'is_new': False,
            'gender': 'WOMEN',
            'type_key': 'bangles',
            'description': 'Handcrafted solid 22K gold kada featuring embossed Goddess Lakshmi motifs flanked by majestic elephants with floral nagas repousse carvings.',
            'specifications': 'Hallmark: BIS 916. Size: 2.6 inches inner diameter (adjustable openable clasp). Finish: Antique Nakashi matte polish.',
        },
        {
            'name': '24K Pure Sovereign Lakshmi Gold Coin (10 Grams)',
            'sku': 'CN-GLD-999-005',
            'category_slug': 'gold-coins-bullion',
            'subcategory_key': 'gold-coins-bullion_10g Sovereign Coins',
            'metal_type': 'GOLD',
            'purity': '24K',
            'gross_weight': Decimal('10.000'),
            'net_weight': Decimal('10.000'),
            'stone_weight': Decimal('0.000'),
            'making_charges': Decimal('850.00'),
            'base_price': Decimal('78500.00'),
            'discount_percent': Decimal('0.00'),
            'stock': 25,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': False,
            'is_trending': True,
            'is_bestseller': True,
            'is_new': False,
            'gender': 'UNISEX',
            'type_key': 'coin',
            'description': '999.9 pure 24K gold investment coin sealed in tamper-evident NABL-accredited security assay blister packaging with unique QR verification code.',
            'specifications': 'Weight: 10.000 grams. Purity: 24 Karat (99.9% Pure). Diameter: 24mm. Obverse: Goddess Lakshmi. Reverse: Royal Monogram & Hallmark.',
        },
        {
            'name': 'Rose Gold Diamond Solitaire Tennis Bracelet',
            'sku': 'BR-DIA-750-006',
            'category_slug': 'diamond-solitaires',
            'subcategory_key': 'diamond-solitaires_Tennis Bracelets',
            'metal_type': 'ROSE_GOLD',
            'purity': '18K',
            'gross_weight': Decimal('14.200'),
            'net_weight': Decimal('12.700'),
            'stone_weight': Decimal('1.500'),
            'making_charges': Decimal('9500.00'),
            'base_price': Decimal('210000.00'),
            'discount_percent': Decimal('12.00'),
            'stock': 3,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': True,
            'is_trending': True,
            'is_bestseller': False,
            'is_new': True,
            'gender': 'WOMEN',
            'type_key': 'bangles',
            'description': 'A graceful continuum of 52 matching brilliant cut diamonds set in 18K warm rose gold prongs with dual safety box clasp.',
            'specifications': 'Diamonds: 52 stones, total 2.60 carats, Color F-G, Clarity VS. Length: 7.0 inches. Metal: 18K Rose Gold (750).',
        },
        {
            'name': 'Temple Heritage Floral Kasu Mala Haram',
            'sku': 'NK-GLD-916-007',
            'category_slug': 'antique-temple',
            'subcategory_key': 'antique-temple_Lakshmi Harams',
            'metal_type': 'GOLD',
            'purity': '22K',
            'gross_weight': Decimal('62.500'),
            'net_weight': Decimal('58.900'),
            'stone_weight': Decimal('3.600'),
            'making_charges': Decimal('18000.00'),
            'base_price': Decimal('435000.00'),
            'discount_percent': Decimal('7.00'),
            'stock': 2,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': True,
            'is_trending': True,
            'is_bestseller': True,
            'is_new': True,
            'gender': 'WOMEN',
            'type_key': 'necklace',
            'description': 'Traditional grand Kasumala necklace comprising 42 embossed coins depicting Lord Balaji and Goddess Padmavathi, culminating in a magnificent nakshi pendant.',
            'specifications': 'Purity: 22K (916). Length: 24 inches long haram. Weight: 62.5g. Gemstones: Natural unheated ruby beads.',
        },
        {
            'name': 'Celestial Starburst 18K Diamond Solitaire Pendant',
            'sku': 'PD-DIA-750-008',
            'category_slug': 'diamond-solitaires',
            'subcategory_key': 'diamond-solitaires_Solitaire Pendants',
            'metal_type': 'DIAMOND',
            'purity': '18K',
            'gross_weight': Decimal('4.800'),
            'net_weight': Decimal('4.400'),
            'stone_weight': Decimal('0.400'),
            'making_charges': Decimal('4500.00'),
            'base_price': Decimal('62000.00'),
            'discount_percent': Decimal('15.00'),
            'stock': 8,
            'availability': 'IN_STOCK',
            'status': 'ACTIVE',
            'is_featured': False,
            'is_trending': True,
            'is_bestseller': True,
            'is_new': True,
            'gender': 'WOMEN',
            'type_key': 'ring',
            'description': 'Dazzling starburst halo pendant featuring a center 0.40 ct solitaire enveloped in a sparkling diamond halo with an 18K yellow gold cable chain included.',
            'specifications': 'Diamond Carat: 0.65 ctw. Chain: 18 inch adjustable gold chain. Certification: SGL International.',
        },
    ]

    media_dir = django.conf.settings.MEDIA_ROOT
    gallery_dir = os.path.join(media_dir, 'products', 'gallery')
    dir_360 = os.path.join(media_dir, 'products', '360')
    banners_dir = os.path.join(media_dir, 'banners')
    os.makedirs(gallery_dir, exist_ok=True)
    os.makedirs(dir_360, exist_ok=True)
    os.makedirs(banners_dir, exist_ok=True)

    created_products = []

    for p_data in products_data:
        cat_slug = p_data.pop('category_slug')
        subcat_key = p_data.pop('subcategory_key')
        type_key = p_data.pop('type_key')
        category = cat_map[cat_slug]
        subcategory = subcat_map.get(subcat_key)

        product, p_created = Product.objects.get_or_create(
            sku=p_data['sku'],
            defaults={
                **p_data,
                'category': category,
                'subcategory': subcategory,
            }
        )
        created_products.append(product)

        # Generate Main Primary Image
        img_name = f"{product.slug}_primary.jpg"
        img_path = os.path.join(gallery_dir, img_name)
        card_img = create_jewellery_card_image(product.name, f"{product.purity} • {product.gross_weight}g", type_key, angle=0)
        card_img.save(img_path, format='JPEG', quality=95)

        # Add or update primary image
        ProductImage.objects.get_or_create(
            product=product,
            is_primary=True,
            defaults={
                'image': f"products/gallery/{img_name}",
                'alt_text': f"{product.name} Primary View",
                'sort_order': 1,
            }
        )

        # Generate Secondary Angle Image for hover flip & gallery
        sec_name = f"{product.slug}_angle.jpg"
        sec_path = os.path.join(gallery_dir, sec_name)
        sec_img = create_jewellery_card_image(product.name, "Alternative View", type_key, angle=45)
        sec_img.save(sec_path, format='JPEG', quality=95)

        ProductImage.objects.get_or_create(
            product=product,
            is_primary=False,
            sort_order=2,
            defaults={
                'image': f"products/gallery/{sec_name}",
                'alt_text': f"{product.name} Detail Angle",
            }
        )

        # Generate 24 MULTI-ANGLE 360-DEGREE FRAMES for Key Featured Products!
        if product.sku in ['RG-DIA-750-002', 'NK-GLD-916-001', 'ER-GLD-916-003']:
            total_frames = 24
            for frame_idx in range(1, total_frames + 1):
                frame_angle = int((frame_idx - 1) * (360.0 / total_frames))
                frame_filename = f"{product.slug}_360_f{frame_idx:02d}.jpg"
                frame_path = os.path.join(dir_360, frame_filename)
                
                # Create actual rotated frame with accurate mathematical angle!
                frame_img = create_jewellery_card_image(
                    product.name,
                    f"360° Angle {frame_angle}°",
                    type_key,
                    width=650,
                    height=650,
                    angle=frame_angle
                )
                frame_img.save(frame_path, format='JPEG', quality=90)

                Product360Image.objects.get_or_create(
                    product=product,
                    frame_number=frame_idx,
                    defaults={
                        'image': f"products/360/{frame_filename}"
                    }
                )
            print(f"[✓] Created 24 true multi-angle 360-degree frames for '{product.name}'")

        # Add customer reviews
        Review.objects.get_or_create(
            product=product,
            user=customer_user,
            defaults={
                'rating': 5,
                'title': "Exquisite craftsmanship and impeccable shine!",
                'comment': f"Purchased this {product.name} for our anniversary. The BIS 916 hallmarking is laser stamped and the weight is exactly as specified. Truly stunning!",
                'is_verified_purchase': True,
                'is_approved': True,
            }
        )

    # 4. Hero Banners
    HeroBanner.objects.get_or_create(
        title="Royal Bridal Trousseau Collection 2026",
        defaults={
            'subtitle': "Handcrafted in 22K Hallmarked Gold, Uncut Polki Diamonds & Basra Pearls",
            'badge_text': "EXCLUSIVE BRIDAL COUTURE",
            'button_text': "Explore Royal Wedding Sets",
            'button_url': "/products/?category=bridal-trousseau",
            'display_order': 1,
            'is_active': True,
        }
    )
    HeroBanner.objects.get_or_create(
        title="Certified Solitaire Diamond Rings",
        defaults={
            'subtitle': "GIA & IGI Authenticated Triple Excellent Cut Solitaires in 18K Gold & Platinum",
            'badge_text': "ETERNAL ROMANCE",
            'button_text': "View Solitaire Collection",
            'button_url': "/products/?category=diamond-solitaires",
            'display_order': 2,
            'is_active': True,
        }
    )
    HeroBanner.objects.get_or_create(
        title="Bespoke Custom Jewellery Studio",
        defaults={
            'subtitle': "Transform your vision into handcrafted gold reality with 3D CAD design & artisan quotes",
            'badge_text': "CUSTOM DESIGN SERVICE",
            'button_text': "Design Your Jewellery",
            'button_url': "/custom-jewellery/",
            'display_order': 3,
            'is_active': True,
        }
    )

    # 5. Customer Testimonials
    Testimonial.objects.get_or_create(
        customer_name="Pooja & Rohan Mehra",
        defaults={
            'city': 'Mumbai, Maharashtra',
            'rating': 5,
            'title': 'Our wedding jewellery was perfection!',
            'review_text': 'We ordered our entire bridal choker and kada set from Aura Gold. The 360-degree view helped us inspect every angle before ordering. The hallmarking and certificate gave us total peace of mind.',
            'is_featured': True,
        }
    )
    Testimonial.objects.get_or_create(
        customer_name="Dr. Vikramaditya Rao",
        defaults={
            'city': 'Hyderabad, Telangana',
            'rating': 5,
            'title': 'Bespoke Diamond Solitaire for proposal',
            'review_text': 'I uploaded a custom design sketch with reference photos on their Custom Jewellery module. Within 24 hours, their artisan sent a detailed quotation and 3D CAD render. She said YES!',
            'is_featured': True,
        }
    )
    Testimonial.objects.get_or_create(
        customer_name="Sunita Singhania",
        defaults={
            'city': 'New Delhi',
            'rating': 5,
            'title': 'Authentic 24K Bullion & Transparent Pricing',
            'review_text': 'Transparent breakdown of gold rates, making charges, and GST. No hidden costs. Insured tamper-proof delivery arrived in 48 hours.',
            'is_featured': True,
        }
    )

    # 6. Sample Custom Order Request with Quotation
    cust_order, cust_created = CustomOrder.objects.get_or_create(
        request_id='CUST-202611-DEMO1',
        defaults={
            'user': customer_user,
            'full_name': 'Ananya Sharma',
            'email': 'customer@gmail.com',
            'phone': '+91 98765 43210',
            'jewellery_type': 'RING',
            'metal_type': 'YELLOW_GOLD',
            'gold_purity': '18K',
            'expected_weight': Decimal('7.500'),
            'preferred_budget': Decimal('95000.00'),
            'ring_size': 'US 6.5 / Indian 13',
            'design_description': 'Victorian style vintage halo ring with an oval Colombian emerald in center, surrounded by round brilliant diamond halo and milgrain filigree engraving on band.',
            'special_instructions': 'Inside band engraving: "Forever & Always 14.02.2026"',
            'status': 'QUOTATION_SENT',
            'admin_notes': 'CAD model prepared. 18K yellow gold casting scheduled upon customer approval.',
        }
    )

    # Create quotation for this custom request
    CustomOrderQuotation.objects.get_or_create(
        custom_order=cust_order,
        quotation_number='QTE-202611-DEMO1',
        defaults={
            'estimated_weight': Decimal('7.200'),
            'metal_rate_applied': Decimal('5590.00'),
            'estimated_metal_cost': Decimal('40248.00'),
            'making_charges': Decimal('12500.00'),
            'stone_charges': Decimal('32000.00'),
            'gst_amount': Decimal('2542.44'),
            'total_estimated_price': Decimal('87290.44'),
            'estimated_making_days': 12,
            'design_notes': '18K Hallmarked 750 Yellow Gold. Central AAA Natural Zambian Emerald 1.25 ct, surrounded by 16 Round Brilliant Diamonds (0.35 ctw, VS-GH).',
            'status': 'SENT',
        }
    )

    # 7. Sample Confirmed Order with Invoice and Tracking
    first_product = created_products[0]
    sample_order, ord_created = Order.objects.get_or_create(
        order_number='GJ-202611-DEMO1',
        defaults={
            'user': customer_user,
            'customer_name': 'Ananya Sharma',
            'customer_email': 'customer@gmail.com',
            'customer_phone': '+91 98765 43210',
            'shipping_address': 'Flat 402, Royale Heritage Palms, MG Road, Opposite Taj Vivanta, Bengaluru, Karnataka - 560001',
            'billing_address': 'Flat 402, Royale Heritage Palms, MG Road, Opposite Taj Vivanta, Bengaluru, Karnataka - 560001',
            'items_total': first_product.final_price,
            'making_charges_total': first_product.making_charges,
            'discount_amount': first_product.discount_amount,
            'tax_amount': round((first_product.final_price * Decimal('3.00')) / Decimal('100.00'), 2),
            'shipping_charges': Decimal('0.00'),
            'grand_total': round(first_product.final_price * Decimal('1.03'), 2),
            'payment_method': 'UPI',
            'payment_status': 'PAID',
            'order_status': 'SHIPPED',
            'tracking_number': 'BLD-GOLD-778942IN',
            'courier_partner': 'BlueDart Apex Gold Insured Courier',
        }
    )

    OrderItem.objects.get_or_create(
        order=sample_order,
        product=first_product,
        defaults={
            'product_name': first_product.name,
            'product_sku': first_product.sku,
            'metal_type': first_product.metal_type,
            'purity': first_product.purity,
            'gross_weight': first_product.gross_weight,
            'net_weight': first_product.net_weight,
            'stone_weight': first_product.stone_weight,
            'unit_price': first_product.final_price,
            'making_charges': first_product.making_charges,
            'quantity': 1,
            'total_price': first_product.final_price,
        }
    )

    Payment.objects.get_or_create(
        order=sample_order,
        transaction_id='TXN-UPI-9948210357',
        defaults={
            'payment_method': 'UPI / QR Code',
            'amount': sample_order.grand_total,
            'status': 'SUCCESS',
            'payment_details': 'UPI Ref: 609214789012@okaxis (Approval Code: APV99120)',
        }
    )

    print("=" * 60)
    print("SUCCESS: Database seeded with luxury jewellery products, 360 multi-angle frames, and sample orders!")
    print("=" * 60)

if __name__ == '__main__':
    main()

