from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from database_setup import Category, Base, CatalogItem, User

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URI)  #'sqlite:///catalog.db'
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
User1 = User(name="Francis", email="franz@udacity.com",
             picture='data/img/blank_user.gif')
session.add(User1)
session.commit()

#Loading category data
with open('data/json/category_data.json') as category_data:    
    category_json = json.load(category_data)

    for cat in category_json['all_categories']:
      category_input = Category(name=str(cat['name']), user_id=1)

      session.add(category_input)
      session.commit()

#Loading item data
with open('data/json/item_data.json') as item_data:    
    item_json = json.load(item_data)

    for item in item_json['all_items']:
      category_input = CatalogItem(name=str(item['name']),description=str(item['description']),pic=str(item['pic']),
      category_id=str(item['category_id']), user_id=1)

      session.add(category_input)
      session.commit()


print "added catalog items!"