from sqlalchemy.orm import sessionmaker

from database_setup import User

###
## Helper functions for creating and getting user information

# User Helper Functions
def createUser(login_session,session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id,session):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email,session):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None