from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Franzee", email="franz@udacity.com",
             picture='/static/img/blank_user.gif')
session.add(User1)
session.commit()

# Category one Soccer
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()

catItem1 = CatalogItem(name="Soccer Jersey", description="Jerseys for the players",
       pic="soccer_jersey.jpg", category=category1, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Boots", description="Boots for the players",
       pic="boot.jpg", category=category1,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Gloves", description="Gloves for the goal keepers",
       pic="gloves.jpeg", category=category1, user_id=1 )

session.add(catItem3)
session.commit()

# Category two SKydiving
category2 = Category(user_id=1, name="Skydiving")

session.add(category2)
session.commit()

catItem1 = CatalogItem(name="Jumpsuit", description="Jumpsuits for the divers",
       pic="jumpsuit.jpeg", category=category2, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Goggles", description="Goggles for the divers",
       pic="goggles.jpeg", category=category2,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Harness", description="Harness for the goal divers",
       pic="harness.jpeg", category=category2, user_id=1 )

session.add(catItem3)
session.commit()

catItem4 = CatalogItem(name="Parachute", description="Parachute for the goal divers",
       pic="parachute.jpeg", category=category2, user_id=1 )

session.add(catItem4)
session.commit()


# Category three Basketball
category3 = Category(user_id=1, name="Basketball")

session.add(category3)
session.commit()

catItem1 = CatalogItem(name="Basketball Jersey", description="Jerseys for the players",
       pic="basketball.jpeg", category=category3, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Sneakers", description="Sneakers for the players",
       pic="nikes.jpg", category=category3,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Ball", description="Ball for the players",
       pic="ball.jpeg", category=category3, user_id=1 )

session.add(catItem3)
session.commit()


# Category four golf
category4 = Category(user_id=1, name="Golf")

session.add(category4)
session.commit()

catItem1 = CatalogItem(name="Golf Clubs", description="Golf clubs for the players",
       pic="golf_clubs.jpeg", category=category4, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Golf Balls", description="Golf balls for the players",
       pic="golf_ball.jpeg", category=category4,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Golf Tees", description="Golf tees for the  players",
       pic="tee.jpeg", category=category4, user_id=1 )

session.add(catItem3)
session.commit()


# Category five Volley ball
category5 = Category(user_id=1, name="Volley Ball")

session.add(category5)
session.commit()

catItem1 = CatalogItem(name="Volley ball hand protector", description="Volley ball hand protector for the players",
       pic="volley_hand_protector.jpeg", category=category5, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Volley ball knee pads", description="Volley ball knee pads for the players",
       pic="volley_knee_pads.jpeg", category=category5,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Volley ball shoes", description="Volley ball shoes for the  players",
       pic="volley_shoes.jpeg", category=category5, user_id=1 )

session.add(catItem3)
session.commit()

catItem4 = CatalogItem(name="Volley ball socks", description="Volley ball socks for the  players",
       pic="volley_socks.jpeg", category=category5, user_id=1 )

session.add(catItem4)
session.commit()




print "added catalog items!"