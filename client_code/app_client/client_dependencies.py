# Dependency Manager for AnvilFusion
class ClientDependencies:
    dependencies = {}
        

    @staticmethod
    def add_dependency(dep_name, dep):
        ClientDependencies.dependencies[dep_name] = dep
        

    @staticmethod
    def remove_dependency(dep_name):
        ClientDependencies.dependencies.pop(dep_name)
        

    @staticmethod
    def get_dependency(dep_name):
        return ClientDependencies.dependencies[dep_name]
    
    
    @staticmethod
    def get_dependencies():
        return ClientDependencies.dependencies
    