# config/__init__.py

import importlib
import os

def get_config(language_code=None):
    """
    Dynamically loads the configuration based on the language code.
    Falls back to the 'fr' config if no language is specified.
    """
    if language_code is None:
        language_code = os.getenv('TARGET_LANGUAGE', 'fr')
        
    try:
        module_name = f".{language_code}"
        config_module = importlib.import_module(module_name, package='config')
        return config_module.Config
    except ImportError:
        raise ImportError(f"Configuration for language '{language_code}' not found. Please create 'config/{language_code}.py'.")

# You can also provide a default config for tools that might not specify a language
DefaultConfig = get_config() 