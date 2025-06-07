from flask import Blueprint, jsonify, request, render_template
from models import db, Recipe, Ingredient

main_bp = Blueprint('main', __name__)

# API маршруты
@main_bp.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Получить список всех рецептов"""
    recipes = Recipe.query.all()
    return jsonify([{
        'id': recipe.id,
        'name': recipe.name,
        'base_servings': recipe.servings
    } for recipe in recipes])

@main_bp.route('/api/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Получить один рецепт по ID с масштабированными ингредиентами"""
    recipe = Recipe.query.get_or_404(recipe_id)

    # Получаем количество порций из параметра запроса
    servings = request.args.get('servings', recipe.servings, type=int)

    return jsonify(recipe.to_dict(servings))

@main_bp.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Получить список всех ингредиентов"""
    ingredients = Ingredient.query.all()
    return jsonify([ingredient.to_dict() for ingredient in ingredients])

# Веб-интерфейс
@main_bp.route('/')
def index():
    """Главная страница с выбором рецепта"""
    return render_template('index.html')

@main_bp.route('/recipe/<int:recipe_id>')
def recipe_page(recipe_id):
    """Страница отображения рецепта"""
    recipe = Recipe.query.get_or_404(recipe_id)
    servings = request.args.get('servings', recipe.servings, type=int)

    recipe_data = recipe.to_dict(servings)

    return render_template('recipe.html', recipe=recipe_data)
