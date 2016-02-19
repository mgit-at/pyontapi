# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.api
    ~~~~~~~~~~~~~~~~~~~

    Base class for all API classes.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import logging

from schtob.pyontapi.errors import PyontapiError, UnknownCommandError

GENERIC_TYPEDEFS = {
    'boolean': bool,
    'integer': int,
    'string': str,
}

GENERIC_TYPES = tuple(GENERIC_TYPEDEFS.values())


class APICommand(object):
    """Representation of API Command for generating API package."""

    def __init__(self, name, elements):
        self.name = name
        self.elements = elements

    def get_package(self):
        """Get package of this API command."""
        return self.name.split('-')[0]

    def get_command_name(self):
        """Get command name of this API command."""
        return '-'.join(self.name.split('-')[1:])

    def get_arguments(self):
        """Yields input elements."""
        for element in self.elements:
            if not element.is_output:
                yield element

    def get_output_fields(self):
        """Yields output elements."""
        for element in self.elements:
            if element.is_output:
                yield element

    def get_py_name(self):
        """Get Python method name for this API command."""
        name = '_'.join(self.name.split('-')[1:])
        if name == 'break' or name[0].isdigit():
            name = '_'.join(self.name.split('-'))
        return name

    def get_py_argument_names(self):
        """Getter for Python arguments. The list contains required arguments at
        the beginning followed by the default arguments.
        """
        for arg in self.get_required_args():
            yield arg
        for arg in self.get_optional_args():
            yield arg

    def get_optional_args(self):
        """Get optional arguments."""
        for arg in self.get_arguments():
            if arg.is_optional:
                yield '`%s` : %s [default = %s]' % (
                    arg.name_to_py(),
                    arg.get_type_name(),
                    repr(arg.get_default())
                )

    def get_required_args(self):
        """Get required arguments."""
        for arg in self.get_arguments():
            if not arg.is_optional:
                yield '`%s` : %s' % (arg.name_to_py(), arg.get_type_name())

    def get_output_fields_and_types(self):
        """Get output field names and types."""
        for field in self.get_output_fields():
            yield '`%s` : %s' % (field.name, field.get_type_name())


class TypeDef(object):
    """API Type class."""

    fields = (
        'name', 'type_name', 'encrypted', 'nonempty', 'is_optional',
        'is_output', 'is_validated', 'is_array',
    )

    def __init__(self, info, var_type):
        self.var_type = var_type
        self.name = info.get('name')
        self.encrypted = info.get('encrypted', False) or False
        self.nonempty = info.get('is-nonempty', False) or False
        self.is_optional = info.get('is-optional', False) or False
        self.is_output = info.get('is-output', False) or False
        self.is_array = ('[]' in info.get('type'))

    def is_generic(self):
        """Check if type is generic."""
        return not isinstance(self.var_type, NamedType)

    def get_type(self):
        """Get type as string. if type is not generic, this returns
        :meth:`var_type.get_py_cls`.
        """
        if self.is_generic():
            return self.var_type
        return self.var_type.get_py_cls()

    def name_to_py(self):
        """Returns a pythonic name for this type."""
        return '_'.join(self.name.split('-'))

    def get_default(self):
        """Get default value."""
        if self.is_array or self.var_type is not str:
            return None
        return ''

    def get_type_name(self):
        """Get type name."""
        if self.is_generic():
            var_type = str(self.var_type)
        else:
            var_type = self.var_type.name
        if self.is_array:
            var_type += '[]'
        return var_type

    def get_py_type_cls(self):
        """Returns the Python class of the type class if the type is used in a
        complex type.
        """
        return NaTypeElement({
            'name': self.name,
            'type': self.get_type(),
            'encrypted': self.encrypted,
            'is-array': self.is_array,
            'nonempty': self.nonempty,
            'is-optional': self.is_optional,
        })

    def get_py_cls(self, value=None):
        """Returns the Python class for this type."""
        if self.is_output:
            return NaField({
                'name': self.name,
                'type': self.get_type(),
                'encrypted': self.encrypted,
                'is-array': self.is_array,
            })
        else:
            return NaArgument(value, {
                'name': self.name,
                'type': self.get_type(),
                'encrypted': self.encrypted,
                'nonempty': self.nonempty,
                'is-optional': self.is_optional,
                'is-array': self.is_array,
            })


class NamedType(object):
    """Class for combined (complex) types."""

    def __init__(self, name, elements):
        self.name = name
        self.elements = elements

    def get_py_cls(self):
        """Returns the Python class for this type."""
        elements = [element.get_py_type_cls() for element in self.elements]
        return NaNamedType(self.name, elements)

    def duplicate(self):
        """Clone this type."""
        return NamedType(self.name, self.elements[:])

    def set_output_value_for_childs(self, output):
        """Sets is_output attribute of all child elements to `output`."""
        for child in self.elements:
            child.is_output = output


def dashed_list(a_list):
    """Return human readable version of list with dashes."""
    return '\n'.join([' - %s' % i for i in a_list])


class NaArgument(object):
    """Argument class for API calls."""

    def __init__(self, value, settings):
        self.value = value
        self.name = settings['name']
        self.var_type = settings['type']
        self.encrypted = settings.get('encrypted', False)
        self.nonempty = settings.get('nonempty', False)
        self.is_optional = settings.get('is-optional', False)
        self.is_array = settings.get('is-array', False)

    def is_set(self):
        """Check if value is set."""
        if self.var_type in GENERIC_TYPES:
            if self.var_type is bool or self.var_type is int:
                return self.value is not None
            elif self.var_type is str:
                return self.value is not None and self.value != ''
            else:
                raise PyontapiError('unknown type %s' % self.var_type)
        elif self.is_array:
            if self.value:
                return True
            return False
        else:
            return self.var_type.is_set(self.value)

    def append_to_doc(self, doc, api):
        """Append argument values to XML query."""
        if not self.is_optional or self.is_set():
            element = doc.createElement(self.name)
            if self.var_type in GENERIC_TYPES:
                text = doc.createTextNode(self.get_content())
                element.appendChild(text)
                api.appendChild(element)
            elif self.is_array:
                for value in self.value:
                    child = self.var_type.append_to_element(doc, value)
                    if child:
                        element.appendChild(child)
                api.appendChild(element)
            else:
                child = self.var_type.append_to_element(doc, self.value)
                if child:
                    element.appendChild(child)
                    api.appendChild(element)

    def get_content(self):
        """Getter for :attr:`value`."""
        if self.encrypted:
            raise NotImplementedError('encryption is not supported yet')
        return str(self.value)


class NaField(object):
    """Output field class."""

    def __init__(self, settings):
        self.name = settings['name']
        self.var_type = settings['type']
        self.encrypted = settings.get('encrypted', False)
        self.is_array = settings.get('is-array', False)

    def get_value(self, parent):
        """Get value out of response."""
        if self.is_array:
            values = []
            for child in parent.getElementsByTagName(self.var_type.name):
                value = self.var_type.get_value(child)
                if value:
                    values.append(value)
            return values
        elif self.var_type in GENERIC_TYPES:
            intermediates = parent.getElementsByTagName(self.name)
            if not intermediates or not intermediates[0].childNodes:
                return self.get_content('')
            child = parent.getElementsByTagName(self.name)[0].childNodes[0]
            return self.get_content(child.data)
        else:
            child = parent.getElementsByTagName(self.name)[0]
            return self.var_type.get_value(child)

    def get_content(self, value):
        """Getter for :attr:`value`."""
        if self.var_type is bool:
            return value == 'true'
        if self.encrypted:
            raise NotImplementedError('encryption is not supported yet')

        # uws: 16.03.2015
        # Error: Handling the API call of the CMode command snapmirror.update
        # Returns '' instead of an 'int' 
        # we return None then
        try:
            return self.var_type(value)
        except:
            return None

class NaNamedType(object):
    """Class for complex ONTAPI types."""

    def __init__(self, name, elements):
        self.name = name
        self.elements = elements

    def append_to_element(self, doc, value):
        """Append element to `doc`.

        If this named type is used as an argument, put the values into the
        XML request.
        """
        entry = doc.createElement(self.name)

        if len(self.elements) == 1 and not self.elements[0].name:
            # if only one element is specified and the name of this
            # element is empty, we need to create a single text node holding
            # the value
            if not value:
                return None
            entry.appendChild(doc.createTextNode(value))
        else:
            for element in self.elements:
                # we assume that ``value`` is a dict and create child elements
                # for each element in the list
                if element.name in value:
                    child = element.append_to_element(doc, value[element.name])
                    if child:
                        entry.appendChild(child)
        return entry

    def get_value(self, parent):
        """Get the value for this field out of `parent`.

        If this named type is used within an output field, read the values out
        of the response and return a dictionary.
        """
        if len(self.elements) == 1 and not self.elements[0].name:
            # if only one element is specified and the name of this
            # element is empty, we need to create a single text node holding
            # the value
            return parent.childNodes[0].data

        value = {}
        for element in self.elements:
            value[element.name] = element.get_value(parent)
        return value

    def is_set(self, value):
        """Check if value is set."""
        if value is None:
            return False
        if len(self.elements) == 1 and not self.elements[0].name:
            if value == '' or value is None:
                return False
            return True
        else:
            for element in self.elements:
                if element.name in value:
                    return True
            return False


class NaTypeElement(object):
    """Class for complex type elements."""

    def __init__(self, settings):
        self.name = settings['name']
        self.var_type = settings['type']
        self.encrypted = settings.get('encrypted', False)
        self.is_array = settings.get('is-array', False)
        self.nonempty = settings.get('nonempty', False)
        self.is_optional = settings.get('is-optional', False)

    def append_to_element(self, doc, value):
        """Append element to `doc`.

        If this named type element is used as an argument, put the values into
        the XML request.
        """
        if not self.name:
            return doc.createTextNode(self.get_content(value))

        element = doc.createElement(self.name)
        if self.var_type in GENERIC_TYPES:
            text = doc.createTextNode(self.get_content(value))
            element.appendChild(text)
        elif self.is_array:
            for val in value:
                child = self.var_type.append_to_element(doc, val)
                element.appendChild(child)
        else:
            child = self.var_type.append_to_element(doc, value[self.name])
            element.appendChild(child)
        return element

    def get_value(self, parent):
        """Get the value for this field out of `parent`.

        if this named type element is used within an output field, read the
        values out of the response.
        """
        children = parent.getElementsByTagName(self.name)
        default = None
        if self.is_array:
            default = []

        if not children:
            return default

        root = children[0]

        if self.is_array:
            if self.var_type in GENERIC_TYPES:
                return [_get_generic_type_value(self.var_type, elem)
                        for elem in root.childNodes]
            else:
                return [self.var_type.get_value(elem)
                        for elem in root.childNodes]
        elif self.var_type in GENERIC_TYPES:
            return _get_generic_type_value(self.var_type, root)
        else:
            return self.var_type.get_value(root)

    def get_content(self, value):
        """Getter for :param:`value`."""
        if self.encrypted:
            raise NotImplementedError('encryption not supported yet')
        return value


def _get_generic_type_value(var_type, elem, default=None):
    """Get the value of a generic type element.
    :param var_type: generic variable type (bool, int, string)
    :param elem: element node
    :param default: default value (default is None)
    """
    if not elem.childNodes:
        return default
    value = elem.childNodes[0].data
    if var_type is bool:
        val = value == 'true'
    else:
        try:
            val = var_type(value)
        except ValueError:
            # Workaround for API bug reported by Julien Garet.
            # The controller-device-path-port info is told to be an
            # integer in the docs but returns a string for
            # ontapi < 1.15
            # Solution: Leave the output as it is, but convert it from
            # unicode to string.
            logging.getLogger('pyontapi').error('Got value error for '
                                                'conversion from %s to type %s',
                                                value, var_type)
            val = str(value)
    return val


class BaseAPI(object):
    """Base class for all ONTAPI classes."""

    def __init__(self, filer, commands=None):
        self._filer = filer
        self._commands = {}
        self._api_methods = {}
        if not commands:
            commands = []
        self.__add_commands(commands)

    def get_command(self, name):
        """Get command by `name`."""
        return self._api_methods[name]

    def invoke_command(self, command, **kwargs):
        """Invoke `command` on filer using `kwargs` as arguments."""
        try:
            fun = self.get_command(command)
        except KeyError:
            raise UnknownCommandError(-1, 'No such api command %s' % command)
        return fun(**kwargs)

    def get_commands(self):
        """Return List of command names."""
        return self._commands.keys()

    def get_command_info(self, command):
        """Get information about command."""
        if command not in self._commands:
            raise KeyError('No such command')
        return getattr(self, command).__doc__

    def __add_commands(self, commands):
        """Adds instance methods for each API command."""
        for command in commands:
            self.__add_command(command)

    def __add_command(self, command):
        """Add instance method for API command."""
        self._commands[command.get_py_name()] = command

        def inner(*args, **kwargs):
            """Invoke API command."""
            if args:
                raise RuntimeError(
                    'API commands accept only keyword arguments!'
                )
            arguments = []
            output_fields = []
            keys = []
            for arg in command.get_arguments():
                field = arg.get_py_cls(
                    kwargs.get(arg.name_to_py(), arg.get_default())
                )
                if arg.name_to_py() in kwargs:
                    keys.append(arg.name_to_py())
                arguments.append(field)
            for field in command.get_output_fields():
                field = field.get_py_cls()
                output_fields.append(field)
            for key in kwargs:
                if key not in keys:
                    raise TypeError("%s() got an unexpected keyword "
                                    "argument '%s'" % (command.get_py_name(),
                                                       key))
            return self._filer.do_api_call(command.name, arguments,
                                           output_fields)

        inner.func_name = str(command.get_py_name())
        inner.__doc__ = """Invoke API command `%(api)s`.

Required Arguments:
%(required_args)s

Optional Arguments:
%(optional_args)s

Output Fields:
%(output_fields)s
""" % {
            'api': command.name,
            'required_args': dashed_list(command.get_required_args()),
            'optional_args': dashed_list(command.get_optional_args()),
            'output_fields': dashed_list(command.get_output_fields_and_types())
        }

        setattr(self, command.get_py_name(), inner)
        self._api_methods[command.get_command_name()] = inner
