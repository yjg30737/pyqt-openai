# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.orm import sessionmaker, declarative_base
#
# # Create a SQLite database file named "myapp.db"
# engine = create_engine('sqlite:///myapp.db')
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()
#
#
# # Define a model class
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     email = Column(String)
#
#     def __repr__(self):
#         return f"<User(name='{self.name}', email='{self.email}')>"
#
#     def save(self):
#         session.add(self)
#         session.commit()
#
# # Create the database tables
# Base.metadata.create_all(engine)