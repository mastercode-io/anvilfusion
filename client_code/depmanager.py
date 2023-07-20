# Dependency Manager for AnvilFusion
import anvil.server


class DepManager:
    dependencies = {}
        

    @staticmethod
    def add_dependency(dep_name, dep):
        DepManager.dependencies[dep_name] = dep
        anvil.server.call('add_dependency', dep_name, dep)
        

    @staticmethod
    def remove_dependency(dep_name):
        DepManager.dependencies.pop(dep_name)
        anvil.server.call('remove_dependency', dep_name)
        

    @staticmethod
    def get_dependency(dep_name):
        return DepManager.dependencies[dep_name]
    
    
    @staticmethod
    def get_dependencies():
        return DepManager.dependencies
    