from .base import SystemAction


class SetCurrentRecipeStepAction(SystemAction):
    def _call_function(self, name, index=None):
        return self._system._set_current_recipe_step(name, index=index)
