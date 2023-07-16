# Helper classes and functions
import anvil


# Dictionary extension that allows dot notation access to keys
@anvil.server.portable_class
@anvil.server.serializable_type
class DotDict(dict):
    def __getattr__(self, item):
        return self[item] if item in self else None

    def __setattr__(self, key, value):
        if key in self:
            self[key] = value if not isinstance(value, dict) else DotDict(value)
        else:
            super(DotDict, self).__setattr__(key, value)

    def __delattr__(self, item):
        if item in self:
            del self[item]
        else:
            super(DotDict, self).__delattr__(item)

    def __getitem__(self, key):
        item = super().__getitem__(key)
        if isinstance(item, dict):
            return DotDict(item)
        elif isinstance(item, list):
            return [DotDict(i) if isinstance(i, dict) else i for i in item]
        else:
            return item


# Basic enumeration class for ORM client
class Enumeration:
    def __init__(self, values, upper_case=True):
        self._values = {}
        self._upper_case = upper_case
        for key, value in values.items():
            attr_name = key.upper() if upper_case is True else key
            self._values[attr_name] = self.Member(attr_name, value)

    def __setattr__(self, name, value):
        if name in ('_values', '_upper_case'):
            return object.__setattr__(self, name, value)
        attr_name = name.upper() if self.upper_case is True else name
        if attr_name in self._values:
            raise AttributeError(f"attribute '{attr_name}' is read-only")
        else:
            super().__setattr__(attr_name, value)

    def __getattr__(self, name):
        if name == '_values':
            return object.__getattribute__(self, '_values')
        if name in self._values:
            return self._values[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __delattr__(self, name):
        if '_values' not in self.__dict__:
            return super().__delattr__(name)
        if name in self._values:
            raise AttributeError(f"attribute '{name}' is read-only")
        else:
            super().__delattr__(name)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {', '.join(self._values.keys())}>"

    def __iter__(self):
        yield from self._values.keys()

    def __len__(self):
        return len(self._values)

    class Member:
        def __init__(self, name, value):
            self.name = name
            self.value = value
            if isinstance(value, dict):
                for key, value in value.items():
                    setattr(self, key, value)

    def __getitem__(self, name):
        if name in self._values:
            return self._values[name]
        raise KeyError(name)
