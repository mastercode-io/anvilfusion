# Dependency Manager for AnvilFusion Client
class DependencyCache:
    dependencies = {}
        

    @staticmethod
    def add_dependency(dep_name, dep):
        DependencyCache.dependencies.get[dep_name] = dep
        

    @staticmethod
    def remove_dependency(dep_name):
        DependencyCache.dependencies.pop(dep_name)
        

    @staticmethod
    def get_dependency(dep_name):
        return DependencyCache.dependencies.get(dep_name, None)
    
    
    @staticmethod
    def dependency_list():
        return [dep_name for dep_name in DependencyCache.dependencies.keys()]
