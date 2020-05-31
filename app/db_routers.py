from django.apps import apps

DEFAULT_DATABASE = 'default'
MONGO_DATABASE = 'mongo'
NO_MIGRATION_DATABASES = [MONGO_DATABASE]


class Router:
    def get_database_name(self, model):
        db_name = getattr(model._meta, 'db', '')
        if db_name not in [DEFAULT_DATABASE, MONGO_DATABASE]:
            raise Exception('Database not defined properly')

        return db_name

    def db_for_read(self, model, **hints):
        return self.get_database_name(model)

    def db_for_write(self, model, **hints):
        return self.get_database_name(model)

    def allow_relation(self, obj1, obj2, **hints):
        return self.get_database_name(obj1) == self.get_database_name(obj2)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return False
        target_model = apps.get_model(app_label, model_name)
        db_name = getattr(target_model._meta, 'db', '')
        return db_name not in NO_MIGRATION_DATABASES
