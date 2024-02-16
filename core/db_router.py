
class AnalyticsRouter:

    route_app_labels = {"analytics"}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "analytics"
        return None