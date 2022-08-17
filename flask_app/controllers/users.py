from pydoc import pager
from flask_app import app, render_template, request, redirect, bcrypt, session, flash
from ..models.favorite import Favorite
from flask_app.models.user import User
from flask_app.models.recipe import Recipe


@app.route('/')
def index():
    if 'user_id' in session:
        print('User is already logged in, displaying dashboard')
        return redirect('/dashboard')
    else:
        return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/')
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password'])
    }
    user_id = User.save(data)
    session['user_id'] = user_id
    session['first_name'] = request.form['first_name']
    return redirect('/dashboard')


@app.route('/login', methods=['POST'])
def login():
    # check if email is in database
    data = {'email': request.form['log_email']}
    user_in_db = User.get_by_email(data)
    if not user_in_db:
        flash('Invalid Email', 'log_email')
        return redirect('/')
    # check password against stored hash
    if not bcrypt.check_password_hash(user_in_db.password, request.form['log_password']):
        flash('Invalid Password', 'log_password')
        return redirect('/')
    # email and password are valid
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        print('User is not in session')
        return redirect('/')
    recipes = Recipe.get_all()
    return render_template('dashboard.html', recipes=recipes, page_title='Dashboard')


@ app.route('/user/recipes')
def user_recipes():
    if 'user_id' not in session:
        print('User is not in session')
        return redirect('/')
    recipes = Recipe.get_all()
    user = User.get_user_with_recipes({'id': session['user_id']})
    non_faves = Favorite.get_all_non_faves({'id': session['user_id']})
    print(non_faves)
    return render_template('userrecipes.html', user=user, recipes=recipes, non_faves=non_faves, page_title='Favorites')


@app.route('/edit/user')
def edit_user():
    user = User.get_one({'id': session['user_id']})
    return render_template('edituser.html', user=user)


@ app.route('/update/user', methods=['POST'])
def update_user():
    if not User.validate_user(request.form):
        return redirect('/edit/user')
    User.update(request.form)
    return redirect("/dashboard")


# @ app.route('/deactivate/<int:id>')
# def deactivate(id):
#     return redirect('/')

# @app.route("/users")
# def show_users():
#     users = User.get_all()
#     # recipes_per_user = []
#     # for user in users:
#     #     recipes_per_user.append(
#     #         User.get_user_with_recipes({'id': user.id}))
#     return render_template('users.html', users=users, page_title='Users')


# @ app.route('/post_user', methods=['POST'])
# def post_user():
#     User.save(request.form)
#     return redirect('/users')
