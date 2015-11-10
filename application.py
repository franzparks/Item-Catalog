import os
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_from_directory
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from flask.ext.sqlalchemy import BaseQuery

from database_setup import Base, Category, CatalogItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import urllib
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from werkzeug import secure_filename

# Set of allowed file extentions for the item images
ALLOWED_EXT = set(['png', 'jpg', 'jpeg', 'gif'])
# pagination constants
# number of categories which can be shown per page
CATEGORIES_PER_PAGE = 5
#number of categories which can be shown per page
ITEMS_PER_PAGE = 3

app = Flask(__name__)

#Photo upload folder --This is where photos are currently served when a user uploads them
app.config['UPLOAD_FOLDER'] = './static/img/'
#Extension for pagination
app.jinja_env.add_extension('jinja2.ext.do')


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Pagination
def paginate(sa_query, page, per_page=20, error_out=True):
  sa_query.__class__ = BaseQuery
  # We can now use BaseQuery methods like .paginate on our SA query
  return sa_query.paginate(page, per_page, error_out)


# Helper to check if photo getting uploaded has the right extention
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXT

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
     
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.data
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You have successfully logged in as %s" % login_session['username'],"success")
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        #return response
        flash("You have logged out successfully!","success")
        return redirect(url_for('showCatalog'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        #return response
        flash("There is an issue with the log out process, please try again", "error")
        return redirect(url_for('showCatalog'))

    


# JSON APIs to view Catalog Information

#Endpoint to get all items in a category
@app.route('/catalog/<category_name>/item/JSON')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    items = session.query(CatalogItem).filter_by(category_name=category_name).all()
    return jsonify(Items=[i.serialize for i in items])

#Endpoint to get a single item in a category
@app.route('/catalog/<category_name>/item/<catalog_item_name>/JSON')
def itemJSON(category_name, catalog_item_name):
    item = session.query(CatalogItem).filter_by(name=catalog_item_name).first()
    return jsonify(item=item.serialize)

#Endpoint to get all catalog categories and items
@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])

#RSS API
#Endpoint to get 15 most recent feeds
@app.route('/catalog/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Catalog Items',feed_url=request.url, url=request.url_root)
   
   items = session.query(CatalogItem).order_by(desc(CatalogItem.category_id))[1:16]
    for item in items:
        feed.add(item.name, unicode(item.rendered_text),
                 content_type='html',
                 author=item.category.user.name,
                 url=make_external(item.url),
                 updated=item.last_update,
                 published=item.published)
    return feed.get_response()    


#RSS API helper to make urls external
def make_external(url):
    return urljoin(request.url_root, url)    


# Show all catalog categories 
@app.route('/', defaults={'page': 1})
@app.route('/catalog/', defaults={'page': 1})
@app.route('/catalog/pg<int:page>')
def showCatalog(page):

    init_categories = session.query(Category).order_by(asc(Category.name))

    categories = paginate(init_categories, page, CATEGORIES_PER_PAGE,False)
    
    init_items = session.query(CatalogItem).order_by(desc(CatalogItem.category_id))

    items = paginate(init_items, page, ITEMS_PER_PAGE,False)

    if 'username' not in login_session:
        return render_template('publicCatalog.html', categories = categories,  items = items)
    else:
        return render_template('catalog.html', categories = categories, items = items)


# Create a new category (authenticated users only)
@app.route('/catalog/new/', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New category %s successfully created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('addCategory.html')


# Edit a category (authenticated and authorized users only)
@app.route('/catalog/<category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    editCategory = session.query(Category).filter_by(name=category_name).first()
    
    if 'username' not in login_session:
        return redirect('/login')
    if editCategory.user_id != login_session['user_id']:
        return render_template('alerts.html',category=editCategory, val = 'edit category')
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
            flash('Category %s successfully edited' % editCategory.name)
            return redirect(url_for('showCatalog', category_name=category_name))
    else:
        return render_template('editCategory.html', category=editCategory)


# Delete a category (authenticated and authorized users only)
@app.route('/catalog/<category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):

    categoryToDelete = session.query(Category).filter_by(name=category_name).first()

    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return render_template('alerts.html',category=categoryToDelete, val = 'delete category')
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog', category_name=category_name))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)



# Show a category item
@app.route('/catalog/<category_name>/',defaults={'page': 1})
@app.route('/catalog/<category_name>/pg<int:page>')
@app.route('/catalog/<category_name>/item/',defaults={'page': 1})
@app.route('/catalog/<category_name>/item/pg<int:page>')
def showCatalogItem(category_name,page):
    category = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category.user_id)
    init_items = session.query(CatalogItem).filter_by(category=category)

    items = paginate(init_items, page, ITEMS_PER_PAGE,False)

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCatalogItem.html', items=items, category=category, creator=creator)
    else:
        return render_template('catalogItem.html', items=items, category=category, creator=creator)


# Show a category item in detail
@app.route('/catalog/<category_name>/item/<item_name>')
def showItemDetails(category_name,item_name):
    category = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category.user_id)
    
    item = session.query(CatalogItem).filter_by(name=item_name).first()

    return render_template('itemDetails.html', item=item, category=category, creator=creator)    


# Create a new category item (authenticated and authorized users only)
@app.route('/catalog/<category_name>/item/new/', methods=['GET', 'POST'])
def addCatalogItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).first()

    if login_session['user_id'] != category.user_id:
        return render_template('alerts.html',category=category, val = 'add item to category')

    if request.method == 'POST':

        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) 
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = "blank_user.gif"    
            
        newItem = CatalogItem(name=request.form['name'], description=request.form['description'], pic=filename, category_id=category.id, user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New catalog item %s successfully added to category' % (newItem.name))
        return redirect(url_for('showCatalogItem', category_name=category_name))
    else:
        return render_template('newCatalogItem.html', category_name=category_name)


# Edit a category item (authenticated and authorized users only)
@app.route('/catalog/<category_name>/item/<item_name>/edit', methods=['GET', 'POST'])
def editCatalogItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(name=item_name).first()
    category = session.query(Category).filter_by(name=category_name).first()
    
    if login_session['user_id'] != category.user_id:
        return render_template('alerts.html',category=category, item=editedItem, val = 'edit item')
            
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        file = request.files['photo']    
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) 
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            editedItem.pic = filename
        session.add(editedItem)
        session.commit()
        flash('Category item %s successfully edited' % (editedItem.name))
        return redirect(url_for('showCatalogItem', category_name=category_name))
    else:
        return render_template('editCatalogItem.html', category_name=category_name, item_name=item_name, item=editedItem)


# Delete a category item (authenticated and authorized users only)
@app.route('/catalog/<category_name>/item/<item_name>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).first()
    itemToDelete = session.query(CatalogItem).filter_by(name=item_name).first()
    if login_session['user_id'] != category.user_id:
        return render_template('alerts.html', category=category,item=itemToDelete, val = 'delete item')

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item %s successfully deleted' % (itemToDelete.name))
        return redirect(url_for('showCatalogItem', category_name=category_name))
    else:
        return render_template('deleteCatalogItem.html', category=category, item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)