import base64
import gzip
import json
from io import BytesIO

from cookbook.helper.ingredient_parser import parse, get_food, get_unit
from cookbook.integration.integration import Integration
from cookbook.models import Recipe, Step, Ingredient


class Paprika(Integration):

    def get_file_from_recipe(self, recipe):
        raise NotImplementedError('Method not implemented in storage integration')

    def get_recipe_from_file(self, file):
        with  gzip.open(file, 'r') as recipe_zip:
            recipe_json = json.loads(recipe_zip.read().decode("utf-8"))

            recipe = Recipe.objects.create(
                name=recipe_json['name'].strip(), description=recipe_json['description'].strip(),
                created_by=self.request.user, internal=True, space=self.request.space)

            step = Step.objects.create(
                instruction=recipe_json['directions'] + '\n\n' + recipe_json['nutritional_info']
            )

            for ingredient in recipe_json['ingredients'].split('\n'):
                amount, unit, ingredient, note = parse(ingredient)
                f = get_food(ingredient, self.request.space)
                u = get_unit(unit, self.request.space)
                step.ingredients.add(Ingredient.objects.create(
                    food=f, unit=u, amount=amount, note=note
                ))

            recipe.steps.add(step)

            self.import_recipe_image(recipe, BytesIO(base64.b64decode(recipe_json['photo_data'])))
            return recipe
