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
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Category one
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()

catItem1 = CatalogItem(name="Jersey", description="Jerseys for the players",
       pic="coming soon", category=category1, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Boots", description="Boots for the players",
       pic="coming soon", category=category1,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Gloves", description="Gloves for the goal keepers",
       pic="coming soon", category=category1, user_id=1 )

session.add(catItem3)
session.commit()

# Category one
category2 = Category(user_id=1, name="Snowboarding")

session.add(category2)
session.commit()

catItem1 = CatalogItem(name="Jersey", description="Jerseys for the players",
       pic="coming soon", category=category2, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Boots", description="Boots for the players",
       pic="coming soon", category=category2,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Gloves", description="Gloves for the goal keepers",
       pic="coming soon", category=category2, user_id=1 )

session.add(catItem3)
session.commit()

# Category one
category3 = Category(user_id=1, name="Basketball")

session.add(category3)
session.commit()

catItem1 = CatalogItem(name="Jersey", description="Jerseys for the players",
       pic="coming soon", category=category3, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Boots", description="Boots for the players",
       pic="coming soon", category=category3,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Gloves", description="Gloves for the goal keepers",
       pic="coming soon", category=category3, user_id=1 )

session.add(catItem3)
session.commit()

# Category one
category4 = Category(user_id=1, name="Golf")

session.add(category4)
session.commit()

catItem1 = CatalogItem(name="Jersey", description="Jerseys for the players",
       pic="coming soon", category=category4, user_id=1)

session.add(catItem1)
session.commit()

catItem2 = CatalogItem(name="Boots", description="Boots for the players",
       pic="coming soon", category=category4,user_id=1)

session.add(catItem2)
session.commit()


catItem3 = CatalogItem(name="Gloves", description="Gloves for the goal keepers",
       pic="coming soon", category=category4, user_id=1 )

session.add(catItem3)
session.commit()





print "added catalog items!"