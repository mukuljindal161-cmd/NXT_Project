import os
import sys
import uuid
import datetime

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api")))

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import User, UserRole, Collection, Document, DocumentChunk, DocumentStatus
from app.security.passwords import get_password_hash
from app.ai.providers import get_ai_provider
from app.config import settings


def seed_database():
    print("Initializing database tables...")
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
            except Exception:
                pass
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Notice on create_all: {e}")

    db = SessionLocal()
    ai_provider = get_ai_provider()

    try:
        print("Checking/Creating demo users...")
        # 1. Admin User
        admin_email = "admin@example.edu"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("AdminPass123!"),
                full_name="Dr. Eleanor Vance (Dean of Academics)",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            print(f"Created Admin: {admin_email} (password: AdminPass123!)")

        # 2. Student User
        student_email = "student@example.edu"
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            student = User(
                email=student_email,
                password_hash=get_password_hash("StudentPass123!"),
                full_name="Alex Morgan (Undergraduate)",
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)
            print(f"Created Student: {student_email} (password: StudentPass123!)")

        db.commit()
        if admin:
            db.refresh(admin)

        print("Checking/Creating standard college collections...")
        collections_data = [
            {
                "name": "Admissions & Enrollment",
                "slug": "admissions",
                "department": "Admissions Office",
                "description": "Application deadlines, eligibility criteria, and enrollment documentation."
            },
            {
                "name": "Academic Regulations & Fees",
                "slug": "academics-fees",
                "department": "Academic Affairs",
                "description": "Curriculum policies, grading scales, examination rules, and semester tuition schedules."
            },
            {
                "name": "Hostel & Residential Life",
                "slug": "hostel",
                "department": "Student Housing",
                "description": "Room allocations, curfew rules, dining hall timings, and resident safety regulations."
            },
            {
                "name": "Library & Research Resources",
                "slug": "library",
                "department": "University Library",
                "description": "Operating hours, book borrowing privileges, digital repository access, and study room reservations."
            }
        ]

        created_collections = {}
        for c_data in collections_data:
            col = db.query(Collection).filter(Collection.slug == c_data["slug"]).first()
            if not col:
                col = Collection(
                    name=c_data["name"],
                    slug=c_data["slug"],
                    department=c_data["department"],
                    description=c_data["description"],
                    is_active=True
                )
                db.add(col)
                db.commit()
                db.refresh(col)
            created_collections[c_data["slug"]] = col

        print("Creating sample college documents and generating embeddings...")

        sample_documents = [
            {
                "title": "Academic Calendar and Fee Regulation Manual 2026-27",
                "filename": "Academic_Fees_Manual_2026.pdf",
                "collection_slug": "academics-fees",
                "chunks": [
                    {
                        "page": 1,
                        "section": "Academic Deadlines & Semester Schedule",
                        "content": "For the Academic Year 2026-27, the Fall semester commences on August 10, 2026. Course registration and add/drop period closes on August 24, 2026. Mid-term examinations will take place from October 12 to October 18, 2026. Final semester examinations are scheduled between December 1 and December 15, 2026."
                    },
                    {
                        "page": 2,
                        "section": "Tuition Fee Structure and Penalties",
                        "content": "The semester tuition fee for undergraduate engineering and science programs is $4,500 per term. The final date for fee payment without penalty is September 15, 2026. Payments submitted between September 16 and September 25 incur a late fee penalty of $50. Accounts unpaid by September 26 will result in temporary course deregistration."
                    },
                    {
                        "page": 3,
                        "section": "Fee Refund & Withdrawal Policy",
                        "content": "Students requesting formal withdrawal from the college prior to the official start of classes receive a 100% refund minus a $100 processing fee. Withdrawals made within the first 14 calendar days of the semester receive an 80% tuition refund. No refunds are granted after 30 calendar days from semester commencement."
                    }
                ]
            },
            {
                "title": "Campus Residential Life & Hostel Code of Conduct",
                "filename": "Hostel_Guidelines_2026.pdf",
                "collection_slug": "hostel",
                "chunks": [
                    {
                        "page": 1,
                        "section": "Hostel Timings & Curfew",
                        "content": "All undergraduate student residences operate with an entry curfew of 10:30 PM Sunday through Thursday, and 11:30 PM on Fridays and Saturdays. Late entry requests must be submitted via the Student Portal at least 6 hours in advance and approved by the resident warden."
                    },
                    {
                        "page": 2,
                        "section": "Dining Hall Hours & Meal Plans",
                        "content": "The Central Dining Hall serves Breakfast from 7:30 AM to 9:30 AM, Lunch from 12:00 PM to 2:00 PM, and Dinner from 7:00 PM to 9:00 PM daily. Special dietary accommodation requests must be registered with the Student Welfare Office by the first Friday of each term."
                    }
                ]
            },
            {
                "title": "University Library Operations & Borrowing Manual",
                "filename": "Library_Guide_2026.pdf",
                "collection_slug": "library",
                "chunks": [
                    {
                        "page": 1,
                        "section": "Library Operating Hours",
                        "content": "The University Central Library is open Monday to Friday from 8:00 AM to 11:00 PM, and Saturday to Sunday from 10:00 AM to 8:00 PM. During official mid-term and final examination weeks, the 2nd Floor Study Commons remains open 24 hours daily with active student card access."
                    },
                    {
                        "page": 2,
                        "section": "Borrowing Privileges & Fines",
                        "content": "Undergraduate students may borrow up to 6 books simultaneously for a duration of 21 days. Graduate students may borrow up to 12 books for 60 days. Overdue items accrue a fine of $0.50 per day per book. Interlibrary loan requests take between 3 to 5 business days."
                    }
                ]
            }
        ]

        for doc_info in sample_documents:
            # Clear previous sample doc to ensure fresh high-dimensional embeddings
            old_doc = db.query(Document).filter(Document.title == doc_info["title"]).first()
            if old_doc:
                db.delete(old_doc)
                db.commit()

            col = created_collections.get(doc_info["collection_slug"])
            doc = Document(
                id=uuid.uuid4(),
                collection_id=col.id if col else None,
                uploaded_by=admin.id if admin else None,
                title=doc_info["title"],
                original_filename=doc_info["filename"],
                mime_type="application/pdf",
                storage_key=f"sample_docs/{doc_info['filename']}",
                file_size=1024 * 50,
                status=DocumentStatus.READY,
                version=1,
                page_count=len(doc_info["chunks"]),
                chunk_count=len(doc_info["chunks"])
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # Generate and add chunks with Gemini text-embedding-004
            for idx, ch_info in enumerate(doc_info["chunks"]):
                emb = ai_provider.embed(ch_info["content"])
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=ch_info["content"],
                    page_number=ch_info["page"],
                    section_title=ch_info["section"],
                    token_count=len(ch_info["content"]) // 4,
                    embedding=emb,
                    metadata_json={"page": ch_info["page"], "section": ch_info["section"]}
                )
                db.add(chunk)

            db.commit()
            print(f"Indexed sample document '{doc.title}' with {len(doc_info['chunks'])} chunks using {settings.EMBEDDING_PROVIDER}.")

        print("\nSeed completed successfully!")
        print("Demo Credentials:")
        print("Admin:   admin@example.edu   / AdminPass123!")
        print("Student: student@example.edu / StudentPass123!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
