# Dependency Manager for AnvilFusion


class DepManager:
    dependencies = {}
        

    @staticmethod
    def add_dependency(self, dep_name, dep):
        self.dependencies[dep_name] = dep
        

    @staticmethod
    def remove_dependency(self, dep_name):
        self.dependencies.pop(dep_name)
        

    @staticmethod
    def get_dependency(self, dep_name):
        return self.dependencies[dep_name]
    