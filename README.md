# Item-Catalog @AUTHOR: FRANCIS PHIRI


Project for Udacity fullstack nano degree program

Udacity Full Stack developer project (Full Specs can be found at: https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true)

HIGHLIGHTS

Develop a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.

Main files in the project

application.py

Contains the implementation for the item-catalog application

database_setup.py

Contains logic to create the database and application domain objects

load_catalog_data.py

Populates the database with the sample data from the category_data.json and item_data.json files

data/category_data.json

Contains initial Category data for the application

data/item_data.json

Contains initial Item data for the application


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

The application can be run in vagrant VM (more details of how to install vagrant on different operating systems in the spec-link provided above)

(The development and testing was done on a Mac with OSX 10.10. It was tested on Chrome 46 and Firefox 41 browsers)
To begin:
1. Clone the project into a directory on your local machine

2. Initalize vagrant in that directory (or move project into a directory which already has vagrant initialized)

3. start vagrant, connect to it and go to the folder which has the project files to start running the project

4. Run database_setup.py to create the database

5. Run load_catalog_data.py to initalize the database with some sample data

6. Run application.py to interact with the application

7. The application can be accessed at: http://localhost:8000/catalog


Some notes on the application:

The application has public features and features that require authentication and authorization

-All  catalog categories and items can be seen whithout logging in. The main catalog page and the category pages support pagination to limit the number of items displayed at a time on the pages

-Currently the application can only be logged in using a google account

-Only logged in users can create,edit and delete categories and category items

-Edit and delete operations are only visible to the owners(creators) of the categories and items

-Error handling is in place for all users (authenticated) who try to edit or delete categories and items while not authorized to do so (e.g by using direct urls)

- The application has JSON and XML APIs

JSON Endpoints:

-http://localhost:8000/catalog/JSON  (for all categories and their items)
-http://localhost:8000/catalog/category_name/item/JSON (for one category and its items)
-http://localhost:8000/catalog/category_name/item/catalog_item_name/JSON (for one item)

XML Endpoints:

-http://localhost:8000/catalog/XML  (for all categories and their items)
-http://localhost:8000/catalog/category_name/item/XML (for one category and its items)
-http://localhost:8000/catalog/category_name/item/catalog_item_name/XML (for one item)



