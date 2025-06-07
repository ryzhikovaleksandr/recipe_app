from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Ассоциативная таблица для связи многие-ко-многим между рецептами и ингредиентами
recipe_ingredients = db.Table('recipe_ingredients',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
    db.Column('quantity', db.Float, nullable=False, default=1.0)
)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    steps = db.Column(db.Text, nullable=False)  # JSON строка со списком шагов
    servings = db.Column(db.Integer, default=1)  # Базовое количество порций

    # Связь многие-ко-многим с ингредиентами
    ingredients = relationship('Ingredient', secondary=recipe_ingredients, backref='recipes')

    def get_steps_list(self):
        """Возвращает список шагов приготовления"""
        import json
        try:
            return json.loads(self.steps)
        except:
            return self.steps.split('\n') if self.steps else []

    def get_ingredients_with_quantities(self):
        """Возвращает ингредиенты с их количествами для данного рецепта"""
        result = []
        for ingredient in self.ingredients:
            # Получаем количество из ассоциативной таблицы
            stmt = db.select(recipe_ingredients.c.quantity).where(
                recipe_ingredients.c.recipe_id == self.id,
                recipe_ingredients.c.ingredient_id == ingredient.id
            )
            quantity = db.session.execute(stmt).scalar() or 1.0

            result.append({
                'ingredient': ingredient,
                'quantity': quantity
            })
        return result

    def to_dict(self, servings=None):
        """Конвертирует рецепт в словарь, опционально масштабируя ингредиенты"""
        servings = servings or self.servings
        scale_factor = servings / self.servings if self.servings > 0 else 1

        ingredients_data = []
        for item in self.get_ingredients_with_quantities():
            ingredient = item['ingredient']
            base_quantity = item['quantity']
            scaled_quantity = base_quantity * scale_factor

            ingredients_data.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'unit': ingredient.unit,
                'quantity': scaled_quantity,
                'base_quantity': base_quantity
            })

        return {
            'id': self.id,
            'name': self.name,
            'steps': self.get_steps_list(),
            'servings': servings,
            'base_servings': self.servings,
            'ingredients': ingredients_data
        }

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # г, мл, шт, ст.л. и т.д.

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit
        }

def add_ingredient_to_recipe(recipe_id, ingredient_id, quantity):
    """Добавляет ингредиент к рецепту с указанным количеством"""
    stmt = recipe_ingredients.insert().values(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        quantity=quantity
    )
    db.session.execute(stmt)

def init_db():
    """Инициализация базы данных с тестовыми данными"""
    db.create_all()

    # Проверяем, есть ли уже данные
    if Recipe.query.count() > 0:
        return

    # Создаем ингредиенты
    ingredients_data = [
        ('Мука', 'г'), ('Яйца', 'шт'), ('Молоко', 'мл'), ('Сахар', 'г'),
        ('Соль', 'г'), ('Масло растительное', 'мл'), ('Мясо говяжье', 'г'),
        ('Лук репчатый', 'шт'), ('Морковь', 'шт'), ('Картофель', 'шт'),
        ('Вода', 'мл'), ('Лавровый лист', 'шт'), ('Перец черный', 'г'),
        ('Рис', 'г'), ('Помидоры', 'шт'), ('Чеснок', 'зубчик')
    ]

    ingredients = []
    for name, unit in ingredients_data:
        ingredient = Ingredient(name=name, unit=unit)
        ingredients.append(ingredient)
        db.session.add(ingredient)

    db.session.commit()

    # Создаем рецепты
    import json

    # Рецепт 1: Блины
    pancake_steps = [
        "Разбить яйца в миску и взбить венчиком",
        "Добавить молоко и перемешать",
        "Просеять муку и добавить в смесь",
        "Добавить сахар и соль, перемешать до однородности",
        "Добавить растительное масло и перемешать",
        "Дать тесту настояться 15-20 минут",
        "Разогреть сковороду и выпекать блины с двух сторон"
    ]

    pancakes = Recipe(
        name="Блины классические",
        steps=json.dumps(pancake_steps, ensure_ascii=False),
        servings=4
    )
    db.session.add(pancakes)
    db.session.commit()

    # Добавляем ингредиенты к блинам
    pancake_ingredients = [
        (1, 200),  # Мука - 200г
        (2, 2),    # Яйца - 2шт
        (3, 500),  # Молоко - 500мл
        (4, 30),   # Сахар - 30г
        (5, 5),    # Соль - 5г
        (6, 30)    # Масло - 30мл
    ]

    for ingredient_id, quantity in pancake_ingredients:
        add_ingredient_to_recipe(pancakes.id, ingredient_id, quantity)

    # Рецепт 2: Борщ
    borscht_steps = [
        "Нарезать мясо кусочками и поставить варить",
        "Очистить и нарезать лук, морковь",
        "Обжарить лук и морковь на растительном масле",
        "Очистить и нарезать картофель",
        "Добавить картофель в кастрюлю с мясом",
        "Добавить обжаренные овощи",
        "Добавить лавровый лист и перец",
        "Варить 20-30 минут до готовности",
        "Посолить по вкусу"
    ]

    borscht = Recipe(
        name="Борщ домашний",
        steps=json.dumps(borscht_steps, ensure_ascii=False),
        servings=6
    )
    db.session.add(borscht)
    db.session.commit()

    # Добавляем ингредиенты к борщу
    borscht_ingredients = [
        (7, 500),  # Мясо - 500г
        (8, 1),    # Лук - 1шт
        (9, 1),    # Морковь - 1шт
        (10, 4),   # Картофель - 4шт
        (11, 2000), # Вода - 2л
        (12, 2),   # Лавровый лист - 2шт
        (13, 3),   # Перец - 3г
        (5, 10),   # Соль - 10г
        (6, 50)    # Масло - 50мл
    ]

    for ingredient_id, quantity in borscht_ingredients:
        add_ingredient_to_recipe(borscht.id, ingredient_id, quantity)

    # Рецепт 3: Плов
    pilaf_steps = [
        "Промыть рис в холодной воде до прозрачности",
        "Нарезать мясо кусочками",
        "Нарезать лук и морковь соломкой",
        "Разогреть масло в казане",
        "Обжарить мясо до золотистой корочки",
        "Добавить лук и жарить до прозрачности",
        "Добавить морковь и жарить 5 минут",
        "Добавить рис и аккуратно перемешать",
        "Залить горячей водой на 2 см выше риса",
        "Добавить специи и чеснок",
        "Варить на сильном огне до испарения воды",
        "Уменьшить огонь и томить под крышкой 30 минут"
    ]

    pilaf = Recipe(
        name="Плов узбекский",
        steps=json.dumps(pilaf_steps, ensure_ascii=False),
        servings=8
    )
    db.session.add(pilaf)
    db.session.commit()

    # Добавляем ингредиенты к плову
    pilaf_ingredients = [
        (14, 500), # Рис - 500г
        (7, 600),  # Мясо - 600г
        (9, 2),    # Морковь - 2шт
        (8, 2),    # Лук - 2шт
        (6, 100),  # Масло - 100мл
        (16, 8),   # Чеснок - 8 зубчиков
        (11, 800), # Вода - 800мл
        (5, 15),   # Соль - 15г
        (13, 5)    # Перец - 5г
    ]

    for ingredient_id, quantity in pilaf_ingredients:
        add_ingredient_to_recipe(pilaf.id, ingredient_id, quantity)

    db.session.commit()
    print("База данных инициализирована с тестовыми данными!")
