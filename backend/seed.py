import asyncio
from database import engine, AsyncSessionLocal, Base
from models import Booking, Service, Review, BookingStatus, ServiceCategory, User


SERVICES_SEED = [
    {
        "id": "srv-1",
        "category": ServiceCategory.hair,
        "title": "Balayage & Couture Cut",
        "price": 180,
        "duration": "120 mins",
        "desc": "Custom hand-painted highlights, gloss toner & luxury blow-dry styling.",
        "img": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": "srv-2",
        "category": ServiceCategory.skin,
        "title": "Hydra-Glow Diamond Facial",
        "price": 145,
        "duration": "75 mins",
        "desc": "Deep pore exfoliation, microdermabrasion & hyaluronic collagen infusion.",
        "img": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": "srv-3",
        "category": ServiceCategory.nails,
        "title": "Luxury Gel Sculpt & Spa",
        "price": 85,
        "duration": "60 mins",
        "desc": "Cuticle restoration, custom gel extensions, and organic rose scrub.",
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": "srv-4",
        "category": ServiceCategory.bridal,
        "title": "Royal Bridal Makeover Suite",
        "price": 350,
        "duration": "180 mins",
        "desc": "HD airbrush bridal makeup, hairstyling, veil styling, and lashes.",
        "img": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": "srv-5",
        "category": ServiceCategory.hair,
        "title": "Brazilian Keratin Smoothing",
        "price": 210,
        "duration": "150 mins",
        "desc": "Frizz elimination, intensive protein seal, and glass shine finish.",
        "img": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": "srv-6",
        "category": ServiceCategory.skin,
        "title": "24K Gold Lift & Anti-Aging",
        "price": 195,
        "duration": "90 mins",
        "desc": "Pure 24k gold leaf masking, LED light therapy & microcurrent lift.",
        "img": "https://images.unsplash.com/photo-1512290900673-7002b5217a29?auto=format&fit=crop&w=400&q=80",
    },
]

USERS_SEED = [
    {"phone": "+1 555-0192", "name": "Sophia Loren", "email": "sophia@example.com"},
    {"phone": "+1 555-0193", "name": "Olivia Wilde", "email": "olivia@example.com"},
    {"phone": "+1 555-0194", "name": "Emma Watson", "email": "emma@example.com"},
]

REVIEWS_SEED = [
    {"name": "Isabella M.", "rating": 5, "comment": "Victoria did an incredible job with my balayage! The lounge ambiance is top tier."},
    {"name": "Chloe K.", "rating": 5, "comment": "The Hydra-Glow facial made my skin radiate for days. Definitely coming back!"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        # Seed services
        result = await session.execute(select(Service))
        if not result.scalars().first():
            for s in SERVICES_SEED:
                session.add(Service(**s))
            await session.commit()
            print(f"  Seeded {len(SERVICES_SEED)} services.")

        # Seed users
        result = await session.execute(select(User))
        if not result.scalars().first():
            for u in USERS_SEED:
                session.add(User(**u))
            await session.commit()
            print(f"  Seeded {len(USERS_SEED)} users.")

        # Seed bookings linked to users
        result = await session.execute(select(Booking))
        if not result.scalars().first():
            users_result = await session.execute(select(User))
            users = {u.phone: u for u in users_result.scalars().all()}

            bookings_seed = [
                {
                    "ref_id": "GLOW-1001",
                    "user_id": users["+1 555-0192"].id,
                    "client_name": "Sophia Loren",
                    "client_email": "sophia@example.com",
                    "client_phone": "+1 555-0192",
                    "service_title": "Balayage & Couture Cut",
                    "price": 180,
                    "stylist_name": "Victoria Vance",
                    "date": "2026-10-22",
                    "time_slot": "10:00 AM",
                    "status": BookingStatus.confirmed,
                },
                {
                    "ref_id": "GLOW-1002",
                    "user_id": users["+1 555-0193"].id,
                    "client_name": "Olivia Wilde",
                    "client_email": "olivia@example.com",
                    "client_phone": "+1 555-0193",
                    "service_title": "Hydra-Glow Diamond Facial",
                    "price": 145,
                    "stylist_name": "Camila Rodriguez",
                    "date": "2026-10-22",
                    "time_slot": "01:00 PM",
                    "status": BookingStatus.pending,
                },
                {
                    "ref_id": "GLOW-1003",
                    "user_id": users["+1 555-0194"].id,
                    "client_name": "Emma Watson",
                    "client_email": "emma@example.com",
                    "client_phone": "+1 555-0194",
                    "service_title": "Royal Bridal Makeover Suite",
                    "price": 350,
                    "stylist_name": "Aiden Dupont",
                    "date": "2026-10-23",
                    "time_slot": "03:00 PM",
                    "status": BookingStatus.confirmed,
                },
            ]
            for b in bookings_seed:
                session.add(Booking(**b))
            await session.commit()
            print(f"  Seeded {len(bookings_seed)} bookings.")

        # Seed reviews
        result = await session.execute(select(Review))
        if not result.scalars().first():
            for r in REVIEWS_SEED:
                session.add(Review(**r))
            await session.commit()
            print(f"  Seeded {len(REVIEWS_SEED)} reviews.")

        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
