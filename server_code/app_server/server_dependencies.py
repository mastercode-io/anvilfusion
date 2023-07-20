# Dependency Manager for AnvilFusion
class ServerDependencies:
    dependencies = {}
        

    @staticmethod
    def add_dependency(dep_name, dep):
        ServerDependencies.dependencies[dep_name] = dep
        

    @staticmethod
    def remove_dependency(dep_name):
        ServerDependencies.dependencies.pop(dep_name)
        

    @staticmethod
    def get_dependency(dep_name):
        return ServerDependencies.dependencies[dep_name]
    
    
    @staticmethod
    def get_dependencies():
        return ServerDependencies.dependencies
    