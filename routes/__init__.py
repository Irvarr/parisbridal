from flask import Blueprint
from routes.main import main
from routes.auth import auth
from routes.registry import registry
from routes.guest import guest
from routes.services import services
from routes.blog import blog

__all__ = ['main', 'auth', 'registry', 'guest', 'services', 'blog']
