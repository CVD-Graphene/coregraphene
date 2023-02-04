"""
Settings and configuration for Graphene Project.

Read values from the module specified by the GRAPHENE_SETTINGS_MODULE environment
variable, and then from coregraphene.conf.global_settings; see the global_settings
for a list of all possible variables.
"""

import importlib
import os

from .global_settings import *


ENVIRONMENT_VARIABLE = "GRAPHENE_SETTINGS_MODULE"


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Settings:
    def __init__(self, settings_module=None):
        if settings_module is None:
            settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            "cls": self.__class__.__name__,
            "settings_module": self.SETTINGS_MODULE,
        }


settings = Settings()
