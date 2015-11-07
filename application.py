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
from werkzeug import secure_filename

ALLOWED_EXT = set(['png', 'jpg', 'jpeg', 'gif'])
# pagination
CATEGORIES_PER_PAGE = 5
ITEMS_PER_PAGE = 3

app = Flask(__name__)

#Photo upload folder
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
@app.route('/catalog/<int:category_id>/item/JSON')
def categoryItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(
        category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/item/<int:catalog_item_id>/JSON')
def itemJSON(category_id, catalog_item_id):
    item = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    return jsonify(item=item.serialize)


@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


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


# Create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCatalog',page=1))
    else:
        return render_template('addCategory.html')


# Edit a catalog category
@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editCategory = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editCategory.user_id != login_session['user_id']:
        return render_template('alerts.html',category=editCategory, val = 'edit category')
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editCategory.name)
            return redirect(url_for('showCatalog',page=1))
    else:
        return render_template('editCategory.html', category=editCategory)


# Delete a catalog category
@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return render_template('alerts.html',category=categoryToDelete, val = 'delete category')
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog', category_id=category_id,page=1))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)



# Show a category item
@app.route('/catalog/<int:category_id>/',defaults={'page': 1})
@app.route('/catalog/<int:category_id>/pg<int:page>')
@app.route('/catalog/<int:category_id>/item/',defaults={'page': 1})
@app.route('/catalog/<int:category_id>/item/pg<int:page>')
def showCatalogItem(category_id,page):
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    init_items = session.query(CatalogItem).filter_by(category_id=category_id)

    items = paginate(init_items, page, ITEMS_PER_PAGE,False)

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCatalogItem.html', items=items, category=category, creator=creator)
    else:
        return render_template('catalogItem.html', items=items, category=category, creator=creator)


# Create a new catalog category item
@app.route('/catalog/<int:category_id>/item/new/', methods=['GET', 'POST'])
def addCatalogItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    print category.name
    if login_session['user_id'] != category.user_id:
        return render_template('alerts.html',category=category, val = 'add item to category')

    if request.method == 'POST':
           
        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) 
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = "blank_user.gif"    
            
        newItem = CatalogItem(name=request.form['name'], description=request.form['description'], pic=filename, category_id=category_id, user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New Catalog Item %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showCatalogItem', category_id=category_id))
    else:
        return render_template('newCatalogItem.html', category_id=category_id)


# Edit a catalog category item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editCatalogItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    
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
        flash('Category Item Successfully Edited')
        return redirect(url_for('showCatalogItem', category_id=category_id))
    else:
        return render_template('editCatalogItem.html', category_id=category_id, item_id=item_id, item=editedItem)


# Delete a category item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(CatalogItem).filter_by(id=item_id).one()
    if login_session['user_id'] != category.user_id:
        return render_template('alerts.html', category=category,item=itemToDelete, val = 'delete item')

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('showCatalogItem', category_id=category_id))
    else:
        return render_template('deleteCatalogItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)