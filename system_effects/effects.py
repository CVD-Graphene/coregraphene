from .base import SystemEffect


class SetCurrentRecipeStepEffect(SystemEffect):
    def _call_function(self, name, index=None):
        return self._system._set_current_recipe_step(name, index=index)


class RecipeStartEffect(SystemEffect):
    def _call_function(self):
        self._system._recipe_history = []
        self._system._recipe_runner.start_recipe()
