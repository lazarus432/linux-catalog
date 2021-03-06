import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps



app = Flask(__name__)
CLIENT_ID = json.loads(
    open('/var/www/catalog/catalog/client_secrets.json', 'r').read())['web']['client_id']
engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# login page
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
            already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: 150px;\
        -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

# disconnect function
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user \
            not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showHome'))
    else:
        response = make_response(json.dumps('Failed to revoke token for \
            given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# returns raw data from database in a readable format
@app.route('/catalog/JSON')
def showItemsJSON():
    category = session.query(Category).all()
    items = session.query(CategoryItem).all()
    return jsonify(CategoryItem = [i.serialize for i in items])

# main page
@app.route('/')
@app.route('/category')
def showHome():
    category=session.query(Category).order_by(Category.name)
    items=session.query(CategoryItem).order_by(desc(CategoryItem.id)).limit(5)
    if 'username' not in login_session:
        return render_template('publicmainpage.html',
            category = category, items = items)
    else:
        return render_template('mainpage.html', category = category,
            items = items)

# create a new category
@app.route('/category/new', methods = ['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'],
            user_id = login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        return render_template('newcategory.html')

# delete a category
@app.route('/category/categories/<int:category_id>/delete/',
methods = ['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    deleteCategory = session.query(Category).filter_by(id = category_id).one()
    if deleteCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not allowed to \
            delete this item. Please create your own category in order to \
            delete.'); }</script><body onload= 'myFunction()'>"
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        return render_template('deletecategory.html',
            category_id = category_id,
            item = deleteCategory)

# function to show items in a category
@app.route('/')
@app.route('/category/categories/<int:category_id>/',
methods = ['GET', 'POST'])
def showItems(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(CategoryItem).filter_by(
        category_id = category_id).all()
    if 'username' not in login_session:
        return render_template('publiccategories.html',
            category_id = category_id, category = category,
            items = items, creator = creator)
    else:
        return render_template('categories.html', category = category,
            category_id = category_id, items = items, creator = creator)


# function to create a new item
@app.route('/category/<int:category_id>/new/', methods = ['GET','POST'])
@login_required
def newItem(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not allowed to \
            add items to this category. Please create your own category to \
            add items.');}</script><body onload = 'myFunction()''>"
    if request.method == 'POST':
        newItem = CategoryItem(name = request.form['name'],
            price = request.form['price'],
            description = request.form['description'],
            itemtype = request.form['itemtype'],
            category_id = category_id,
            user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('newitem.html', category_id = category_id)

# function to edit an item
@app.route('/category/<int:category_id>/<int:item_id>/edit/',
methods = ['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    editItem = session.query(CategoryItem).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(id = category_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not allowed to \
        edit items to this category. Please create your own category to edit \
        items.');}</script><body onload = 'myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['price']:
            editItem.price = request.form['price']
        if request.form['description']:
            editItem.description = request.form['description']
        session.add(editItem)
        session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('edititem.html', category_id = category_id,
            item_id = item_id, i = editItem)


# function to delete an item
@app.route('/category/<int:category_id>/<int:item_id>/delete/',
methods = ['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
    deleteItem = session.query(CategoryItem).filter_by(id = item_id).one()
    if deleteItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not allowed to \
            delete this item. Please create your own item in order to \
            delete.');}</script><body onload= 'myFunction()'>"
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('deleteitem.html', category_id = category_id,
            item = deleteItem)

# user helper functions
def createUser(login_session):
    newUser = User(name = login_session['username'],
        email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None



if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='127.0.0.1', port=8000)
