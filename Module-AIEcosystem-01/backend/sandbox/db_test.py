from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Database Connection Setup
DATABASE_URL = "postgresql+psycopg2://admin:password123@localhost:5433/school_db"

# Create Engine and Session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Create Model for 'students' table
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    major = Column(String)

def test_database_operations():
    print("Starting PostgreSQL and SQLAlchemy tests...")
    # [Work 4.1] Create table
    print("\n--- 1. Creating Table ---")
    Base.metadata.create_all(bind=engine)
    print("Successfully created 'students' table.")

    session = SessionLocal()

    try:
        # [Work 4.2] Insert data
        print("\n--- 2. Inserting Data ---")
        new_student = Student(id=1, name="Somchai", age=20, major="Computer Engineering")
        session.add(new_student)
        session.commit()
        print(f"Successfully inserted student data: {new_student.name}")

        # [Work 4.3] Update data
        print("\n--- 3. Updating Data ---")
        student = session.query(Student).filter(Student.id == 1).first()
        if student:
            student.major = "Artificial Intelligence"
            session.commit()
            print(f"Successfully updated major for {student.name} to {student.major}")

        # [Work 4.4] Delete data
        print("\n--- 4. Deleting Data ---")
        student_to_delete = session.query(Student).filter(Student.id == 1).first()
        if student_to_delete:
            session.delete(student_to_delete)
            session.commit()
            print("Successfully deleted student with ID 1.")

    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()
    finally:
        session.close()

    #  [Work 4.5] Delete table
    print("\n--- 5. Deleting Table ---")
    Base.metadata.drop_all(bind=engine)
    print("Successfully dropped 'students' table.")


if __name__ == "__main__":
    test_database_operations()