from flask_app import app, render_template, request, redirect, session
from flask_app.models.recipe import Recipe
from flask_app.models.user import User


@app.route('/recipes')
def all_recipes():
    recipes = Recipe.get_all()
    return render_template('allrecipes.html', recipes=recipes, page_title='Recipes')


@app.route('/new/recipe')
def new_recipe():
    return render_template('recipeform.html', page_title='New Recipe', user=User.get_one({'id': session['user_id']}), action='post')


@app.route('/post/recipe', methods=['POST'])
def post_recipe():
    recipe_id = Recipe.save(request.form)
    return redirect(f'/recipe/{recipe_id}')


@app.route('/recipe/<int:id>')
def show_recipe(id):
    recipe = Recipe.get_one({'id': id})
    return render_template('recipe.html', recipe=recipe, page_title=recipe.name)


@app.route('/edit/<int:id>')
def edit_recipe(id):
    recipe = Recipe.get_one({'id': id})
    if not recipe.user_id == session['user_id']:
        return redirect('/')
    return render_template('recipeform.html', recipe=recipe, page_title='Edit Recipe', action='update', user=User.get_one({'id': session['user_id']}))


@app.route('/update/recipe', methods=['POST'])
def update_recipe():
    Recipe.update(request.form)
    return redirect(f"/recipe/{request.form['id']}")


@app.route('/delete/<int:id>')
def delete_recipe(id):
    Recipe.delete({'id': id})
    return redirect('/')

# @app.route('/recipes/<int:id>')
# def show_recipe(id):
#     recipe = Recipe.get_recipe_with_users({'id': id})
#     return render_template('recipeusers.html', recipe=recipe)
