# Item-Catalog
Project for Udacity fullstack nano degree program

Udacity Full Stack developer project (Full Specs can be found at: https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true)

Highlights

Develop a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.

Main files in the project

application.py

Contains the implementation for the item-catalog application

database_setup.py

Contains logic to create the database and application domain objects

catalog.py

Contains the sample data for the application


Folders in the project:

Templates folder:

Contains template files which are used for display

Static folder:

Contains css files

Static/img folder:

Is the upload folder for the  images which are uploaded by the application

Photos-for-testing:

Contains sample images which can be used to test the appliction. This acts as a convenient source folder when trying out the application instead of looking for photos online


How to run the application:

The application can be run in vagrant VM (more details of how to install vagrant in the spec-link provided above)

1. Run database_setup.py to create the database

2. Run catalog.py to initalize the database with some sample data

3. Run application.py to interact with the application

4. The application can be accessed at: http://localhost:8000/catalog


Some notes on the application:

The application has public features and features that require authentication and authorization

-All  catalog categories and items can be seen whithout logging in. The main catalog page and the category pages support pagination to limit the number of items on displayed at a time on the pages

-Currently the application can only be logged in using a google account

-Only logged in users can create,edit and delete categories and category items

-Edit and delete operations are only visible to the owners(creators) of the categories and items

-Error handling is in place for all users (authenticated) who try to edit or delete categories and items while not authorized to do so (e.g by using direct urls)

- The application has JSON and RSS feed APIs

JSON:

-http://localhost:8000/catalog/JSON  (for all categories and their items)
-http://localhost:8000/catalog/<category>/item/JSON (for one category and its items)
-http://localhost:8000/catalog/<category>/item/<catalog_item_name>/JSON (for one item)

RSS:
-http://localhost:8000//catalog/recent.atom (for the most recent catalog item feeds)





