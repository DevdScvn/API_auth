from sqladmin import ModelView

from core.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]
    can_delete = False
    column_details_exclude_list = [User.password]

