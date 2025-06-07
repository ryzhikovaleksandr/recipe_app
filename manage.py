#!/usr/bin/env python3
"""
Утилиты для управления базой данных
"""

import sys
import json
from app import create_app
from models import db, Recipe, Ingredient, add_ingredient_to_recipe

def init_database():
    """Инициализация базы данных"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("База данных создана!")

def reset_database():
    """Полная очистка и пересоздание базы данных"""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("База данных очищена и пересоздана!")

def add_sample_data():
    """Добавить тестовые данные"""
    app = create_app()
    with app.app_context():
        # Проверяем, есть ли уже данные
        if Recipe.query.count() > 0:
            print("Тестовые данные уже существуют!")
            return

        from models import init_db
        init_db()
        print("Тестовые данные добавлены!")

def add_recipe_interactive():
    """Интерактивное добавление рецепта"""
    app = create_app()
    with app.app_context():
        print("\n=== Добавление нового рецепта ===")

        # Основная информация
        name = input("Название рецепта: ").strip()
        if not name:
            print("Название не может быть пустым!")
            return

        try:
            servings = int(input("Базовое количество порций: "))
        except ValueError:
            print("Количество порций должно быть числом!")
            return

        # Шаги приготовления
        print("\nВведите шаги приготовления (пустая строка для завершения):")
        steps = []
        step_num = 1
        while True:
            step = input(f"Шаг {step_num}: ").strip()
            if not step:
                break
            steps.append(step)
            step_num += 1

        if not steps:
            print("Рецепт должен содержать хотя бы один шаг!")
            return

        # Создаем рецепт
        recipe = Recipe(
            name=name,
            steps=json.dumps(steps, ensure_ascii=False),
            servings=servings
        )
        db.session.add(recipe)
        db.session.commit()

        print(f"\nРецепт '{name}' создан с ID: {recipe.id}")

        # Добавляем ингредиенты
        print("\n=== Добавление ингредиентов ===")
        print("Доступные ингредиенты:")
        ingredients = Ingredient.query.all()
        for ing in ingredients:
            print(f"  {ing.id}: {ing.name} ({ing.unit})")

        print("\nВведите ингредиенты (ID количество, например: 1 200)")
        print("Пустая строка для завершения:")

        while True:
            ing_input = input("Ингредиент: ").strip()
            if not ing_input:
                break

            try:
                parts = ing_input.split()
                if len(parts) != 2:
                    print("Формат: ID количество")
                    continue

                ing_id = int(parts[0])
                quantity = float(parts[1])

                ingredient = Ingredient.query.get(ing_id)
                if not ingredient:
                    print(f"Ингредиент с ID {ing_id} не найден!")
                    continue

                add_ingredient_to_recipe(recipe.id, ing_id, quantity)
                print(f"Добавлен: {ingredient.name} - {quantity} {ingredient.unit}")

            except ValueError:
                print("Некорректный формат! Используйте: ID количество")

        db.session.commit()
        print(f"\nРецепт '{name}' успешно создан!")

def list_recipes():
    """Показать все рецепты"""
    app = create_app()
    with app.app_context():
        recipes = Recipe.query.all()
        if not recipes:
            print("Рецепты не найдены!")
            return

        print("\n=== Список рецептов ===")
        for recipe in recipes:
            print(f"ID: {recipe.id}")
            print(f"Название: {recipe.name}")
            print(f"Порций: {recipe.servings}")
            print(f"Ингредиентов: {len(recipe.get_ingredients_with_quantities())}")
            print("-" * 40)

def show_recipe_details(recipe_id):
    """Показать подробности рецепта"""
    app = create_app()
    with app.app_context():
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            print(f"Рецепт с ID {recipe_id} не найден!")
            return

        print(f"\n=== {recipe.name} ===")
        print(f"Базовое количество порций: {recipe.servings}")

        print("\nИнгредиенты:")
        for item in recipe.get_ingredients_with_quantities():
            ingredient = item['ingredient']
            quantity = item['quantity']
            print(f"  {ingredient.name}: {quantity} {ingredient.unit}")

        print("\nШаги приготовления:")
        for i, step in enumerate(recipe.get_steps_list(), 1):
            print(f"  {i}. {step}")

def add_ingredient():
    """Добавить новый ингредиент"""
    app = create_app()
    with app.app_context():
        print("\n=== Добавление нового ингредиента ===")

        name = input("Название ингредиента: ").strip()
        if not name:
            print("Название не может быть пустым!")
            return

        unit = input("Единица измерения (г, мл, шт и т.д.): ").strip()
        if not unit:
            print("Единица измерения не может быть пустой!")
            return

        # Проверяем, существует ли такой ингредиент
        existing = Ingredient.query.filter_by(name=name, unit=unit).first()
        if existing:
            print(f"Ингредиент '{name}' с единицей '{unit}' уже существует!")
            return

        ingredient = Ingredient(name=name, unit=unit)
        db.session.add(ingredient)
        db.session.commit()

        print(f"Ингредиент '{name}' добавлен с ID: {ingredient.id}")

def main():
    """Главная функция для работы с утилитами"""
    if len(sys.argv) < 2:
        print("Использование: python manage.py <команда>")
        print("\nДоступные команды:")
        print("  init          - Создать базу данных")
        print("  reset         - Очистить и пересоздать базу данных")
        print("  sample-data   - Добавить тестовые данные")
        print("  add-recipe    - Добавить рецепт интерактивно")
        print("  add-ingredient - Добавить ингредиент")
        print("  list          - Показать все рецепты")
        print("  show <id>     - Показать подробности рецепта")
        return

    command = sys.argv[1]

    if command == "init":
        init_database()
    elif command == "reset":
        reset_database()
    elif command == "sample-data":
        add_sample_data()
    elif command == "add-recipe":
        add_recipe_interactive()
    elif command == "add-ingredient":
        add_ingredient()
    elif command == "list":
        list_recipes()
    elif command == "show":
        if len(sys.argv) < 3:
            print("Укажите ID рецепта: python manage.py show <id>")
            return
        try:
            recipe_id = int(sys.argv[2])
            show_recipe_details(recipe_id)
        except ValueError:
            print("ID должен быть числом!")
    else:
        print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main()
