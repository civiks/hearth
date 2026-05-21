"""Seed demo data.

Usage:
    uv run python -m backend.seed

Idempotent: skips entries that already exist. Run `alembic upgrade head` first.

Mirrors the marketplace shape rendered by the frontend — 8 categories, 18
services, ~30 professionals across the categories, ~10 customers, ~40
historical requests in mixed statuses. Photos via Unsplash, avatars via
DiceBear (deterministic seed-based URLs, hotlinked).
"""

import secrets
import urllib.parse
from datetime import datetime, timedelta
from random import Random

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import session_scope
from backend.core.security import hash_password
from backend.models import (
    ApprovalStatus,
    Role,
    Service,
    ServiceProfessional,
    ServiceRequest,
    ServiceStatus,
    User,
)


def _photo(unsplash_id: str) -> str:
    return (
        f"https://images.unsplash.com/photo-{unsplash_id}?w=800&auto=format&fit=crop"
    )


def _avatar(name: str) -> str:
    seed = urllib.parse.quote(name)
    return f"https://api.dicebear.com/9.x/notionists/svg?seed={seed}"


# ----------------------------------------------------------------------------
# Reference data — mirrors frontend/src/lib/demo/fixtures.ts so the marketplace
# looks identical whether the frontend is hitting the real backend or running
# in VITE_DEMO=1 static mode.
# ----------------------------------------------------------------------------

CATEGORIES = [
    "Plumbing",
    "Electrical",
    "Carpentry",
    "Cleaning",
    "Painting",
    "AC & Appliance",
    "Pest Control",
    "Gardening",
]

CATEGORY_IMAGES = {
    "Plumbing": ["1585704032915-c3400ca199e7", "1607472586893-edb57bdc0e39"],
    "Electrical": ["1565608087341-404b25492fee", "1558002038-1055907df827"],
    "Carpentry": ["1504148455328-c376907d081c", "1567538096630-e0c55bd6374c"],
    "Cleaning": ["1581578731548-c64695cc6952", "1527515637462-cff94eecc1ac"],
    "Painting": ["1562259949-e8e7689d7828", "1589939705384-5185137a7f0f"],
    "AC & Appliance": ["1505691938895-1758d7feb511", "1599619351208-3e6c839d6828"],
    "Pest Control": ["1593696140826-c58b021acf8b", "1583947215259-38e31be8751f"],
    "Gardening": ["1416879595882-3373a0480b5b", "1523348837708-15d4a09cfac2"],
}

# Service names from the original (pre-marketplace) seed. These get nuked along
# with their FK dependents at the start of a re-seed so the demo lands on the
# new 18-service catalogue instead of 23 mismatched rows.
LEGACY_SERVICE_NAMES = {
    "Plumbing",
    "Electrical Work",
    "Carpentry",
    "House Cleaning",
    "Painting",
}

SERVICE_DEFS = [
    # Plumbing
    ("Tap & Pipe Repair", "Plumbing", "Fix leaks, replace faucets, and resolve pressure issues. Same-day service.", 199, 60),
    ("Bathroom Fitting", "Plumbing", "Toilet, basin, shower installation and replacement by certified plumbers.", 549, 120),
    ("Water Tank Cleaning", "Plumbing", "Mechanical scrubbing and chlorine treatment for overhead and underground tanks.", 799, 180),
    # Electrical
    ("Wiring & Switches", "Electrical", "Switchboard repair, new wiring runs, and earthing checks. Licensed work.", 249, 75),
    ("Fan & Light Installation", "Electrical", "Ceiling fans, chandeliers, and LED panel installation with cleanup.", 299, 60),
    ("Inverter & UPS Service", "Electrical", "Battery health check, inverter installation, and load balancing.", 449, 90),
    # Carpentry
    ("Furniture Assembly", "Carpentry", "Flat-pack assembly, modular kitchen fittings, and on-site adjustments.", 349, 90),
    ("Door & Window Repair", "Carpentry", "Hinge replacement, alignment fixes, locks and handle replacement.", 249, 60),
    ("Custom Shelving", "Carpentry", "Made-to-measure shelves, wall units, and storage solutions in wood or MDF.", 1499, 240),
    # Cleaning
    ("Deep Home Cleaning", "Cleaning", "Full-home deep clean: dusting, mopping, kitchen and bathroom sanitization.", 1899, 300),
    ("Bathroom Cleaning", "Cleaning", "Tile descaling, fixture polishing, and grout treatment for sparkling results.", 499, 90),
    ("Sofa & Carpet Cleaning", "Cleaning", "Shampoo extraction and steam cleaning for upholstery, sofas, and rugs.", 899, 120),
    # Painting
    ("Interior Painting", "Painting", "Per-room interior painting with premium emulsion. Includes prep and cleanup.", 2499, 480),
    ("Exterior & Texture Painting", "Painting", "Weatherproof exterior coats and decorative textures by experienced painters.", 4999, 720),
    # AC & Appliance
    ("AC Service & Repair", "AC & Appliance", "Filter clean, gas top-up, leak fix. Split and window AC supported.", 549, 90),
    ("Refrigerator & Washing Machine Repair", "AC & Appliance", "On-site diagnosis and repair for major appliance brands.", 449, 60),
    # Pest Control
    ("Cockroach & Ant Treatment", "Pest Control", "Odourless gel-based treatment safe for kids and pets. 3-month warranty.", 899, 90),
    # Gardening
    ("Lawn & Garden Care", "Gardening", "Mowing, hedge trimming, weeding, and seasonal planting recommendations.", 699, 120),
]

PRO_NAMES = [
    "Ravi Kumar", "Priya Sharma", "Arjun Reddy", "Sunita Iyer",
    "Vikram Singh", "Kavya Menon", "Rohan Desai", "Lakshmi Nair",
    "Aditya Rao", "Meena Pillai", "Karthik Patel", "Anjali Krishnan",
    "Suresh Mehta", "Divya Bhat", "Nitin Joshi", "Sneha Kulkarni",
    "Rajesh Pillai", "Pooja Hegde", "Manoj Verma", "Shreya Murthy",
    "Ashok Naidu", "Geeta Rao", "Yogesh Kapoor", "Rekha Shenoy",
    "Devendra Achar", "Latha Rao", "Hemant Bhatt", "Madhuri Pai",
    "Surya Prasad", "Anita Kamath",
]

CUSTOMER_NAMES = [
    "Aakash Gupta", "Nisha Banerjee", "Tarun Saxena", "Ishita Roy",
    "Varun Kashyap", "Tanvi Malhotra", "Sanjay Bose", "Pranita Joshi",
    "Aravind Krishnamurthy", "Meher Chopra",
]

BIOS = [
    "Certified specialist with a focus on residential work and clean finishes.",
    "Started as an apprentice at 18, now leads small teams across Bangalore.",
    "Known for tidy workspaces and clear before-after explanations to customers.",
    "Trained at NSDC; carries own equipment and follows safety protocols strictly.",
    "Friendly, on-time, and patient. Speaks Kannada, English, and Hindi.",
    "Worked with a major service brand for 4+ years before going independent.",
    "Specializes in quick turnaround jobs without compromising on quality.",
    "Background in commercial maintenance; brings industrial-grade precision to homes.",
    "Honest pricing, no upselling. Prefers to fix rather than replace when possible.",
    "Repeat customers across HSR Layout and Indiranagar; rated highly for follow-ups.",
]

AREAS = [
    ("Indiranagar", "560038"),
    ("Koramangala", "560034"),
    ("HSR Layout", "560102"),
    ("Whitefield", "560066"),
    ("Jayanagar", "560011"),
    ("Marathahalli", "560037"),
    ("BTM Layout", "560029"),
    ("Electronic City", "560100"),
]


# ----------------------------------------------------------------------------
# Idempotent ensure_* helpers
# ----------------------------------------------------------------------------


def ensure_role(session: Session, name: str, description: str) -> Role:
    role = session.scalars(select(Role).where(Role.name == name)).first()
    if role is None:
        role = Role(name=name, description=description)
        session.add(role)
        session.flush()
    return role


def ensure_user(
    session: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    address: str | None,
    pincode: str | None,
    role: Role,
    avatar_url: str | None = None,
    rating: float | None = None,
    review_count: int | None = None,
    date_created: datetime | None = None,
) -> User:
    user = session.scalars(select(User).where(User.email == email)).first()
    if user is not None:
        # Top up marketplace fields if a previous seed (pre-migration) left them empty
        dirty = False
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
            dirty = True
        if rating is not None and user.rating is None:
            user.rating = rating
            dirty = True
        if review_count is not None and user.review_count is None:
            user.review_count = review_count
            dirty = True
        if dirty:
            session.flush()
        return user
    user = User(
        email=email,
        password=hash_password(password),
        full_name=full_name,
        address=address,
        pincode=pincode,
        fs_uniquifier=secrets.token_hex(16),
        active=True,
        is_blocked=False,
        date_created=date_created or datetime.now(),
        avatar_url=avatar_url,
        rating=rating,
        review_count=review_count,
    )
    user.roles.append(role)
    session.add(user)
    session.flush()
    return user


def ensure_service(
    session: Session,
    *,
    name: str,
    base_price: float,
    time_required: int,
    description: str,
    category: str,
    image_url: str,
    rating: float,
    review_count: int,
) -> Service:
    service = session.scalars(select(Service).where(Service.name == name)).first()
    if service is None:
        service = Service(
            name=name,
            base_price=base_price,
            time_required=time_required,
            description=description,
            category=category,
            image_url=image_url,
            rating=rating,
            review_count=review_count,
        )
        session.add(service)
        session.flush()
        return service
    # Backfill marketplace fields on prior seeds
    dirty = False
    if service.category != category:
        service.category = category
        dirty = True
    if not service.image_url:
        service.image_url = image_url
        dirty = True
    if service.rating is None:
        service.rating = rating
        dirty = True
    if service.review_count is None:
        service.review_count = review_count
        dirty = True
    if dirty:
        session.flush()
    return service


def ensure_professional(
    session: Session,
    *,
    user: User,
    service: Service,
    experience: int,
    description: str,
    approval_status: ApprovalStatus,
) -> ServiceProfessional:
    existing = session.scalars(
        select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
    ).first()
    if existing is not None:
        return existing
    pro = ServiceProfessional(
        user_id=user.id,
        service_id=service.id,
        experience=experience,
        description=description,
        approval_status=approval_status.value,
    )
    session.add(pro)
    session.flush()
    return pro


# ----------------------------------------------------------------------------
# Main seeder
# ----------------------------------------------------------------------------


def seed(session: Session) -> None:
    rng = Random(2026_05_20)  # deterministic seed for stable demo data

    # Drop legacy 5-service catalog before inserting the new 18-service one.
    # Deletes are bounded to exact legacy names; FK dependents cascade.
    legacy_services = session.scalars(
        select(Service).where(Service.name.in_(LEGACY_SERVICE_NAMES))
    ).all()
    for svc in legacy_services:
        if svc.image_url:
            # Migrated forward already — leave intact.
            continue
        # Find ServiceProfessionals for this service and delete their requests + the
        # ServiceProfessional row (keep the User account).
        pros_for_service = session.scalars(
            select(ServiceProfessional).where(ServiceProfessional.service_id == svc.id)
        ).all()
        pro_ids = [p.id for p in pros_for_service]
        if pro_ids:
            session.execute(
                ServiceRequest.__table__.delete().where(
                    ServiceRequest.professional_id.in_(pro_ids)
                )
            )
        session.execute(
            ServiceRequest.__table__.delete().where(ServiceRequest.service_id == svc.id)
        )
        for p in pros_for_service:
            session.delete(p)
        session.delete(svc)
    if legacy_services:
        session.flush()

    admin_role = ensure_role(session, "admin", "Administrator")
    pro_role = ensure_role(session, "professional", "Professional")
    user_role = ensure_role(session, "user", "User")
    session.commit()

    # Admin
    ensure_user(
        session,
        email="admin@email.com",
        password="admin",
        full_name="Demo Admin",
        address="MG Road",
        pincode="560001",
        role=admin_role,
        avatar_url=_avatar("Demo Admin"),
    )

    # Legacy customers (kept for backward compatibility with user01..user05)
    legacy_customers = [
        ("user01@email.com", "user01", "Priya Sharma", "456 Jayanagar", "560041"),
        ("user02@email.com", "user02", "Amit Patel", "789 Indiranagar", "560038"),
        ("user03@email.com", "user03", "Sneha Reddy", "321 Koramangala", "560034"),
        ("user04@email.com", "user04", "Mahesh Saini", "123 MG Road", "560001"),
        ("user05@email.com", "user05", "Rohan Iyer", "12 Whitefield", "560066"),
    ]
    for email, pw, name, addr, pin in legacy_customers:
        ensure_user(
            session,
            email=email,
            password=pw,
            full_name=name,
            address=addr,
            pincode=pin,
            role=user_role,
            avatar_url=_avatar(name),
        )

    # Extended customer roster
    extended_customers: list[User] = []
    for i, name in enumerate(CUSTOMER_NAMES):
        area, pin = AREAS[i % len(AREAS)]
        email = name.lower().replace(" ", ".") + "@example.com"
        u = ensure_user(
            session,
            email=email,
            password="demo123",
            full_name=name,
            address=f"{10 + i * 3}, {area}",
            pincode=pin,
            role=user_role,
            avatar_url=_avatar(name),
        )
        extended_customers.append(u)

    session.commit()

    # Services
    services: list[Service] = []
    for i, (name, category, desc, price, time_required) in enumerate(SERVICE_DEFS):
        images = CATEGORY_IMAGES[category]
        image_url = _photo(images[i % len(images)])
        rating = round(3.9 + ((i * 7) % 11) * 0.1, 1)
        review_count = 24 + ((i * 37) % 360)
        svc = ensure_service(
            session,
            name=name,
            base_price=float(price),
            time_required=time_required,
            description=desc,
            category=category,
            image_url=image_url,
            rating=rating,
            review_count=review_count,
        )
        services.append(svc)

    session.commit()

    # Legacy professional logins kept for compatibility (plumber@, electrician@, etc.).
    # Each maps to one of the new richer services.
    legacy_pros = [
        ("plumber@email.com", "Ramesh Yadav", "Tap & Pipe Repair", 8, BIOS[0], ApprovalStatus.APPROVED),
        ("electrician@email.com", "Suresh Verma", "Wiring & Switches", 5, BIOS[5], ApprovalStatus.APPROVED),
        ("carpenter@email.com", "Mohan Singh", "Furniture Assembly", 10, BIOS[1], ApprovalStatus.APPROVED),
        ("cleaner@email.com", "Lakshmi Devi", "Deep Home Cleaning", 3, BIOS[6], ApprovalStatus.APPROVED),
        ("painter@email.com", "Mahendra Khanna", "Interior Painting", 4, BIOS[3], ApprovalStatus.PENDING),
    ]
    approved_pros: list[ServiceProfessional] = []
    for i, (email, name, service_name, exp, bio, approval) in enumerate(legacy_pros):
        service = next(s for s in services if s.name == service_name)
        area, pin = AREAS[i % len(AREAS)]
        user = ensure_user(
            session,
            email=email,
            password="pass123",
            full_name=name,
            address=f"{20 + i * 5}, {area}",
            pincode=pin,
            role=pro_role,
            avatar_url=_avatar(name),
            rating=round(4.0 + ((i * 11) % 9) * 0.1, 1),
            review_count=40 + ((i * 17) % 250),
        )
        pro = ensure_professional(
            session,
            user=user,
            service=service,
            experience=exp,
            description=bio,
            approval_status=approval,
        )
        if approval == ApprovalStatus.APPROVED:
            approved_pros.append(pro)

    # Extended professional roster (~30 more, deterministic, spread across services)
    extended_pros: list[ServiceProfessional] = []
    for i, name in enumerate(PRO_NAMES):
        service = services[(i + 2) % len(services)]
        area, pin = AREAS[i % len(AREAS)]
        # ~1 pending, ~1 rejected per roster for variety; rest approved
        approval = (
            ApprovalStatus.PENDING
            if i == len(PRO_NAMES) - 1
            else ApprovalStatus.REJECTED
            if i == len(PRO_NAMES) - 2
            else ApprovalStatus.APPROVED
        )
        email = name.lower().replace(" ", ".") + "@demo.local"
        if email == "ravi.kumar@demo.local":
            email = "ravi.kumar.pro@demo.local"  # avoid clash with legacy
        user = ensure_user(
            session,
            email=email,
            password="demo123",
            full_name=name,
            address=f"{30 + i * 4}, {area}",
            pincode=pin,
            role=pro_role,
            avatar_url=_avatar(name),
            rating=round(3.8 + ((i * 11) % 12) * 0.1, 1),
            review_count=8 + ((i * 17) % 332),
        )
        pro = ensure_professional(
            session,
            user=user,
            service=service,
            experience=1 + ((i * 7) % 12),
            description=BIOS[i % len(BIOS)],
            approval_status=approval,
        )
        if approval == ApprovalStatus.APPROVED:
            extended_pros.append(pro)

    session.commit()

    # Historical service requests
    existing_request = session.scalars(select(ServiceRequest)).first()
    if existing_request is None:
        all_customers = session.scalars(
            select(User).join(User.roles).where(Role.name == "user")
        ).all()
        all_approved_pros = approved_pros + extended_pros

        status_plan = (
            [ServiceStatus.COMPLETED] * 22
            + [ServiceStatus.IN_PROGRESS] * 2
            + [ServiceStatus.ACCEPTED] * 6
            + [ServiceStatus.REQUESTED] * 4
            + [ServiceStatus.CANCELLED] * 6
        )

        for i, status in enumerate(status_plan):
            service = services[i % len(services)]
            customer = all_customers[i % len(all_customers)]
            matching = [p for p in all_approved_pros if p.service_id == service.id]
            pro: ServiceProfessional | None = None
            if status in (ServiceStatus.ACCEPTED, ServiceStatus.IN_PROGRESS, ServiceStatus.COMPLETED):
                pro = (
                    matching[i % len(matching)]
                    if matching
                    else all_approved_pros[i % len(all_approved_pros)]
                )

            if status == ServiceStatus.COMPLETED:
                days_ago = 4 + ((i * 3) % 80)
            elif status == ServiceStatus.CANCELLED:
                days_ago = 6 + ((i * 5) % 50)
            elif status == ServiceStatus.IN_PROGRESS:
                days_ago = 1
            elif status == ServiceStatus.ACCEPTED:
                days_ago = (i % 4) + 1
            else:  # REQUESTED — future or just-now
                days_ago = (i % 3)

            date_of_request = (datetime.now() - timedelta(days=days_ago)).date()
            scheduled = (
                datetime.now() + timedelta(days=(i % 5) + 1, hours=i % 8)
                if status == ServiceStatus.REQUESTED
                else datetime.now() - timedelta(days=days_ago, hours=i % 8)
            )
            address = customer.address or f"{10 + i}, {AREAS[i % len(AREAS)][0]}"
            pincode = customer.pincode or AREAS[i % len(AREAS)][1]
            session.add(
                ServiceRequest(
                    service_id=service.id,
                    customer_id=customer.id,
                    professional_id=pro.id if pro else None,
                    service_status=status.value,
                    scheduled_time=scheduled,
                    address=address,
                    pincode=pincode,
                    remarks="Please call before arriving." if i % 3 == 0 else None,
                    date_of_request=date_of_request,
                    date_of_completion=datetime.now() - timedelta(days=max(0, days_ago - 1))
                    if status == ServiceStatus.COMPLETED
                    else None,
                )
            )

        session.commit()

    # Touch the rng so linters don't flag it as unused (used only for future randomization).
    _ = rng


def main() -> None:
    with session_scope() as session:
        seed(session)
    print("Seed complete.")


if __name__ == "__main__":
    main()
