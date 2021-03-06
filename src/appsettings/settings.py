# -*- coding: utf-8 -*-

"""
Settings module.

This module defines the different type checkers and settings classes.
"""

import importlib
import itertools
import warnings

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinLengthValidator, MinValueValidator

from .validators import DictKeysTypeValidator, DictValuesTypeValidator, TypeValidator, ValuesTypeValidator


# Type checkers ===============================================================
class TypeChecker(object):
    """
    Type checker base class.

    A type checker is a simple class that can be called when instantiated in
    order to validate an object against some conditions. A simple type checker
    will only check the type of the object. More complex type checkers can
    be created by inheriting from this base class.
    """

    def __init__(self, base_type=None):
        """
        Initialization method.

        Args:
            base_type (type): the type to check against value's type.
        """
        warnings.warn("Checkers are deprecated in favor of validators.", DeprecationWarning)
        self.base_type = base_type

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (object): the value to check.

        Raises:
            ValueError: if value is not type base_type.
        """
        if not isinstance(value, self.base_type):
            raise ValueError("%s must be %s, not %s" % (name, self.base_type, value.__class__))


class BooleanTypeChecker(TypeChecker):
    """Boolean type checker."""

    def __init__(self):
        """Initialization method."""
        super(BooleanTypeChecker, self).__init__(base_type=bool)


class IntegerTypeChecker(TypeChecker):
    """Integer type checker."""

    def __init__(self, minimum=None, maximum=None):
        """
        Initialization method.

        Args:
            minimum (int): a minimum value (included).
            maximum (int): a maximum value (included).
        """
        super(IntegerTypeChecker, self).__init__(base_type=int)
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (int): the value to check.

        Raises:
            ValueError: if value is not type int.
            ValueError: if value is less than minimum.
            ValueError: if value is more than maximum.
        """
        super(IntegerTypeChecker, self).__call__(name, value)
        if isinstance(self.minimum, int):
            if value < self.minimum:
                raise ValueError("%s must be greater or equal %s" % (name, self.minimum))
        if isinstance(self.maximum, int):
            if value > self.maximum:
                raise ValueError("%s must be less or equal %s" % (name, self.maximum))


class FloatTypeChecker(TypeChecker):
    """Float type checker."""

    def __init__(self, minimum=None, maximum=None):
        """
        Initialization method.

        Args:
            minimum (float): a minimum value (included).
            maximum (float): a maximum value (included).
        """
        super(FloatTypeChecker, self).__init__(base_type=float)
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (float): the value to check.

        Raises:
            ValueError: if value is not type float.
            ValueError: if value is less than minimum.
            ValueError: if value is more than maximum.
        """
        super(FloatTypeChecker, self).__call__(name, value)
        if isinstance(self.minimum, float):
            if value < self.minimum:
                raise ValueError("%s must be greater or equal %s" % (name, self.minimum))
        if isinstance(self.maximum, float):
            if value > self.maximum:
                raise ValueError("%s must be less or equal %s" % (name, self.maximum))


# Iterable type checkers ------------------------------------------------------
class IterableTypeChecker(TypeChecker):
    """
    Iterable type checker.

    Inherit from this class to create type checkers that support iterable
    object checking, with item type, minimum and maximum length, and
    allowed emptiness.
    """

    def __init__(self, iter_type, item_type=None, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            iter_type (type): the type of the iterable object.
            item_type (type): the type of the items inside the object.
            min_length (int): a minimum length (included).
            max_length (int): a maximum length (included).
            empty (bool): whether emptiness is allowed.
        """
        super(IterableTypeChecker, self).__init__(base_type=iter_type)
        self.item_type = item_type
        self.min_length = min_length
        self.max_length = max_length
        self.empty = empty

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (iterable): the value to check.

        Raises:
            ValueError: if value is not type iter_type.
            ValueError: if any item in value is not type item_type.
            ValueError: if value's length is less than min_length.
            ValueError: if value's length is more than max_length.
            ValueError: if value's length is 0 and emptiness is not allowed.
        """
        super(IterableTypeChecker, self).__call__(name, value)
        if isinstance(self.item_type, type):
            if not all(isinstance(o, self.item_type) for o in value):
                raise ValueError("All elements of %s must be %s" % (name, self.item_type))
        if isinstance(self.min_length, int):
            if len(value) < self.min_length:
                raise ValueError("%s must be longer than %s (or equal)" % (name, self.min_length))
        if isinstance(self.max_length, int):
            if len(value) > self.max_length:
                raise ValueError("%s must be shorter than %s (or equal)" % (name, self.max_length))
        if len(value) == 0 and not self.empty:
            raise ValueError("%s must not be empty" % name)


class StringTypeChecker(IterableTypeChecker):
    """String type checker."""

    def __init__(self, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            min_length (int): minimum length of the string (included).
            max_length (int): maximum length of the string (included).
            empty (bool): whether empty string is allowed.
        """
        super(StringTypeChecker, self).__init__(
            iter_type=str, min_length=min_length, max_length=max_length, empty=empty
        )


class ListTypeChecker(IterableTypeChecker):
    """List type checker."""

    def __init__(self, item_type=None, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            item_type (type): the type of the items inside the list.
            min_length (int): minimum length of the list (included).
            max_length (int): maximum length of the list (included).
            empty (bool): whether empty list is allowed.
        """
        super(ListTypeChecker, self).__init__(
            iter_type=list, item_type=item_type, min_length=min_length, max_length=max_length, empty=empty
        )


class SetTypeChecker(IterableTypeChecker):
    """Set type checker."""

    def __init__(self, item_type=None, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            item_type (type): the type of the items inside the set.
            min_length (int): minimum length of the set (included).
            max_length (int): maximum length of the set (included).
            empty (bool): whether empty set is allowed.
        """
        super(SetTypeChecker, self).__init__(
            iter_type=set, item_type=item_type, min_length=min_length, max_length=max_length, empty=empty
        )


class TupleTypeChecker(IterableTypeChecker):
    """Tuple type checker."""

    def __init__(self, item_type=None, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            item_type (type): the type of the items inside the tuple.
            min_length (int): minimum length of the tuple (included).
            max_length (int): maximum length of the tuple (included).
            empty (bool): whether empty tuple is allowed.
        """
        super(TupleTypeChecker, self).__init__(
            iter_type=tuple, item_type=item_type, min_length=min_length, max_length=max_length, empty=empty
        )


# Dict type checkers ----------------------------------------------------------
class DictTypeChecker(TypeChecker):
    """Dict type checker."""

    def __init__(self, key_type=None, value_type=None, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            key_type (type): the type of the dict keys.
            value_type (type): the type of the dict values.
            min_length (int): minimum length of the dict (included).
            max_length (int): maximum length of the dict (included).
            empty (bool): whether empty dict is allowed.
        """
        super(DictTypeChecker, self).__init__(base_type=dict)
        self.key_type = key_type
        self.value_type = value_type
        self.min_length = min_length
        self.max_length = max_length
        self.empty = empty

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (dict): the value to check.

        Raises:
            ValueError: if value is not type dict.
            ValueError: if any key in value is not type key_type.
            ValueError: if any value in value is not type value_type.
            ValueError: if value's length is less than min_length.
            ValueError: if value's length is more than max_length.
            ValueError: if value's length is 0 and emptiness is not allowed.
        """
        super(DictTypeChecker, self).__call__(name, value)
        if isinstance(self.key_type, type):
            if not all(isinstance(o, self.key_type) for o in value.keys()):
                raise ValueError("All keys of %s must be %s" % (name, self.key_type))
        if isinstance(self.value_type, type):
            if not all(isinstance(o, self.value_type) for o in value.values()):
                raise ValueError("All values of %s must be %s" % (name, self.value_type))
        if isinstance(self.min_length, int):
            if len(value) < self.min_length:
                raise ValueError("%s must be longer than %s (or equal)" % (name, self.min_length))
        if isinstance(self.max_length, int):
            if len(value) > self.max_length:
                raise ValueError("%s must be shorter than %s (or equal)" % (name, self.max_length))
        if len(value) == 0 and not self.empty:
            raise ValueError("%s must not be empty" % name)


# Complex type checkers -------------------------------------------------------
class ObjectTypeChecker(StringTypeChecker):
    """
    Object type checker.

    Actually only check if the given value is a string.

    TODO: maybe check that value is a valid Python path
    (https://stackoverflow.com/questions/47537921).
    TODO: maybe check that the object actually exists
    (https://stackoverflow.com/questions/14050281).
    """

    def __init__(self, empty=True):
        """
        Initialization method.

        Args:
            empty (bool):
        """
        super(ObjectTypeChecker, self).__init__(empty=empty)

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (str): the value to check.

        Raises:
            ValueError: if value is not type str.
        """
        super(ObjectTypeChecker, self).__call__(name, value)
        # TODO: maybe check that value is a valid Python path
        # https://stackoverflow.com/questions/47537921
        # TODO: maybe check that the object actually exists
        # https://stackoverflow.com/questions/14050281


# Settings ====================================================================
class Setting(object):
    """
    Base setting class.

    The setting's name and prefix are used to specify the variable name to
    look for in the project settings. The default value is returned only if
    the variable is missing and the setting is not required. If the setting
    is missing and required, trying to access it will raise an AttributeError.

    When accessing a setting's value, the value is first fetched from the
    project settings, then passed to a transform function that will return it
    modified (or not). By default, no transformation is applied.

    The call_default parameter tells if we should try to call the given
    default value before returning it. This allows to give lambdas or callables
    as default values. The transform_default parameter tells if we should
    transform the default value as well through the transform method.

    Class attributes:
        default_validators (list of callables): Default set of validators for the setting.
    """

    default_validators = ()
    checker = None  # Disable checker by default

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        checker=None,
        validators=(),
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (object): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            checker (callable):
                an instance of type checker or any callable object accepting
                two arguments (name, value).
                This argument is deprecated.
            validators (list of callables): list of additional validators to use.
        """
        self.name = name
        self.default = default
        self.call_default = call_default
        self.transform_default = transform_default
        self.required = required
        self.prefix = prefix
        self.parent_setting = None

        if checker is not None:
            warnings.warn("Checkers are deprecated in favor of validators.", DeprecationWarning)
            self.checker = checker

        self.validators = list(itertools.chain(self.default_validators, validators))

    def _reraise_if_required(self, err):
        if self.required:
            if isinstance(err, KeyError):
                raise KeyError("%s setting is missing required item %s" % (self.parent_setting.full_name, err))
            else:
                raise AttributeError("%s setting is required and %s" % (self.full_name, err))

    @property
    def full_name(self):
        """
        Property to return the full name of the setting.

        Returns:
            str: upper prefix + upper name.
        """
        return self.prefix.upper() + self.name.upper()

    @property
    def default_value(self):
        """
        Property to return the default value.

        If the default value is callable and call_default is True, return
        the result of default(). Else return default.

        Returns:
            object: the default value.
        """
        if callable(self.default) and self.call_default:
            return self.default()
        return self.default

    @property
    def raw_value(self):
        """
        Property to return the variable defined in ``django.conf.settings``.

        Returns:
            object: the variable defined in ``django.conf.settings``.

        Raises:
            AttributeError: if the variable is missing.
            KeyError: if the item is missing from nested setting.
        """
        if self.parent_setting is not None:
            return self.parent_setting.raw_value[self.full_name]
        else:
            return getattr(settings, self.full_name)

    @property
    def value(self):
        """
        Property to return the transformed raw or default value.

        This property is a simple shortcut for get_value().

        Returns:
            object: the transformed raw value.
        """
        return self.get_value()

    def get_value(self):
        """
        Return the transformed raw or default value.

        If the variable is missing from the project settings, and the setting
        is required, re-raise an AttributeError. If it is not required,
        return the (optionally transformed) default value.

        Returns:
            object: the transformed raw value.
        """
        try:
            value = self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
            default_value = self.default_value
            if self.transform_default:
                return self.transform(default_value)
            return default_value
        else:
            return self.transform(value)

    def validate(self, value):
        """Run custom validation on the setting value.

        By default, no additional validation is performed.

        Raises:
            ValidationError: if the validation fails.

        """
        pass

    def run_validators(self, value):
        """Run the validators on the setting value."""
        errors = []
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as error:
                errors.extend(error.messages)
        if errors:
            raise ValidationError(errors)

    def check(self):
        """
        Run the setting checker against the setting raw value.

        Raises:
            AttributeError: if the setting is missing and required.
            ValueError: if the raw value is invalid.
        """
        try:
            value = self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
        else:
            if self.checker:
                self.checker(self.full_name, value)
            try:
                self.validate(value)
                self.run_validators(value)
            except ValidationError as error:
                raise ValueError("Setting {} has an invalid value: {}".format(self.full_name, error))

    def transform(self, value):
        """
        Return a transformed value.

        By default, no transformation is done.

        Args:
            value (object):

        Returns:
            object: the transformed value.
        """
        return value


class BooleanSetting(Setting):
    """Boolean setting."""

    default_validators = (TypeValidator(bool),)

    def __init__(
        self,
        name="",
        default=True,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (bool): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
        """
        super(BooleanSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )


class IntegerSetting(Setting):
    """Integer setting."""

    default_validators = (TypeValidator(int),)

    def __init__(
        self,
        name="",
        default=0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        minimum=None,
        maximum=None,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (int): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            minimum (int): a minimum value (included).
            maximum (int): a maximum value (included).
        """
        super(IntegerSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if minimum is not None:
            self.validators.append(MinValueValidator(minimum))
        if maximum is not None:
            self.validators.append(MaxValueValidator(maximum))


class PositiveIntegerSetting(IntegerSetting):
    """Positive integer setting."""

    def __init__(
        self,
        name="",
        default=0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        maximum=None,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (int): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            maximum (int): a maximum value (included).
        """
        super(PositiveIntegerSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
            minimum=0,
            maximum=maximum,
        )


class FloatSetting(IntegerSetting):
    """Float setting."""

    default_validators = (TypeValidator(float),)

    def __init__(
        self,
        name="",
        default=0.0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        minimum=None,
        maximum=None,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (float): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            minimum (int): a minimum value (included).
            maximum (int): a maximum value (included).
        """
        super(FloatSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
            minimum=minimum,
            maximum=maximum,
        )


class PositiveFloatSetting(FloatSetting):
    """Positive float setting."""

    def __init__(
        self,
        name="",
        default=0.0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        maximum=None,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (float): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            maximum (int): a maximum value (included).
        """
        super(PositiveFloatSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
            minimum=0,
            maximum=maximum,
        )


# Iterable settings -----------------------------------------------------------
class IterableSetting(Setting):
    """Iterable setting."""

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        item_type=None,
        min_length=None,
        max_length=None,
        empty=None,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (iterable): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super(IterableSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if item_type is not None:
            self.validators.append(ValuesTypeValidator(item_type))
        if empty is not None:
            warnings.warn("Empty argument is deprecated, use min_length instead.", DeprecationWarning)
            if not empty:
                min_length = 1
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))


class StringSetting(Setting):
    """String setting."""

    default_validators = (TypeValidator(str),)

    def __init__(
        self,
        name="",
        default="",
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        min_length=None,
        max_length=None,
        empty=True,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (str): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super(StringSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if empty is not None:
            warnings.warn("Empty argument is deprecated, use min_length instead.", DeprecationWarning)
            if not empty:
                min_length = 1
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))


class ListSetting(IterableSetting):
    """List setting."""

    default_validators = (TypeValidator(list),)

    def __init__(self, name="", default=list, *args, **kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (list): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super(ListSetting, self).__init__(name=name, default=default, *args, **kwargs)


class SetSetting(IterableSetting):
    """Set setting."""

    default_validators = (TypeValidator(set),)

    def __init__(self, name="", default=set, *args, **kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (set): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super(SetSetting, self).__init__(name=name, default=default, *args, **kwargs)


class TupleSetting(IterableSetting):
    """Tuple setting."""

    default_validators = (TypeValidator(tuple),)

    def __init__(self, name="", default=tuple, *args, **kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (tuple): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super(TupleSetting, self).__init__(name=name, default=default, *args, **kwargs)


# Dict settings ---------------------------------------------------------------
class DictSetting(Setting):
    """Dict setting."""

    default_validators = (TypeValidator(dict),)

    def __init__(
        self,
        name="",
        default=dict,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        key_type=None,
        value_type=None,
        min_length=None,
        max_length=None,
        empty=None,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (dict): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            key_type: the type of the dict keys.
            value_type (type): the type of dict values.
            min_length (int): Noop. Deprecated.
            max_length (int): Noop. Deprecated.
            empty (bool): whether empty iterable is allowed. Deprecated in favor of MinLengthValidator.
        """
        super(DictSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if key_type is not None:
            self.validators.append(DictKeysTypeValidator(key_type))
        if value_type is not None:
            self.validators.append(DictValuesTypeValidator(value_type))
        if empty is not None:
            warnings.warn("Empty argument is deprecated, use MinLengthValidator instead.", DeprecationWarning)
            self.validators.append(MinLengthValidator(1))
        if min_length is not None:
            warnings.warn("Argument min_length does nothing and is deprecated.", DeprecationWarning)
        if max_length is not None:
            warnings.warn("Argument max_length does nothing and is deprecated.", DeprecationWarning)


# Complex settings ------------------------------------------------------------
class ObjectSetting(Setting):
    """
    Object setting.

    This setting allows to return an object given its Python path (a.b.c).
    """

    default_validators = (TypeValidator(str),)

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        min_length=None,
        max_length=None,
        empty=True,
    ):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (object): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            min_length (int): Noop. Deprecated.
            max_length (int): Noop. Deprecated.
            empty (bool): Noop. Deprecated.
        """
        super(ObjectSetting, self).__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if min_length is not None:
            warnings.warn("Argument min_length does nothing and is deprecated.", DeprecationWarning)
        if max_length is not None:
            warnings.warn("Argument max_length does nothing and is deprecated.", DeprecationWarning)
        if empty is not None:
            warnings.warn("Argument empty does nothing and is deprecated.", DeprecationWarning)

    def transform(self, path):
        """
        Transform a path into an actual Python object.

        The path can be arbitrary long. You can pass the path to a package,
        a module, a class, a function or a global variable, as deep as you
        want, as long as the deepest module is importable through
        ``importlib.import_module`` and each object is obtainable through
        the ``getattr`` method. Local objects will not work.

        Args:
            path (str): the dot-separated path of the object.

        Returns:
            object: the imported module or obtained object.
        """
        if path is None or not path:
            return None

        obj_parent_modules = path.split(".")
        objects = [obj_parent_modules.pop(-1)]

        while True:
            try:
                parent_module_path = ".".join(obj_parent_modules)
                parent_module = importlib.import_module(parent_module_path)
                break
            except ImportError:
                if len(obj_parent_modules) == 1:
                    raise ImportError("No module named '%s'" % obj_parent_modules[0])
                objects.insert(0, obj_parent_modules.pop(-1))

        current_object = parent_module
        for obj in objects:
            current_object = getattr(current_object, obj)
        return current_object


# Nested settings -------------------------------------------------------------
class NestedSetting(DictSetting):
    """Nested setting."""

    def __init__(self, settings, *args, **kwargs):
        """
        Initialization method.

        Args:
            settings (dict): subsettings.
            name (str): the name of the setting.
            default (dict): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            key_type: the type of the dict keys.
            value_type (type): the type of dict values.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super(NestedSetting, self).__init__(*args, **kwargs)
        for subname, subsetting in settings.items():
            if subsetting.name == "":
                subsetting.name = subname
            subsetting.parent_setting = self
        self.settings = settings

    def get_value(self):
        """
        Return dictionary with values of subsettings.

        Returns:
            dict: values of subsettings.
        """
        try:
            self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
            default_value = self.default_value
            if self.transform_default:
                return self.transform(default_value)
            return default_value
        else:
            # If setting is defined, load values of all subsettings.
            value = {}
            for key, subsetting in self.settings.items():
                value[key] = subsetting.get_value()
            return value

    def check(self):
        """
        Run the setting checker against the setting raw value.

        Raises:
            AttributeError: if the setting is missing and required.
            ValueError: (or other Exception) if the raw value is invalid.
        """
        super(NestedSetting, self).check()
        errors = []
        for subsetting in self.settings.values():
            try:
                subsetting.check()
            except ValidationError as error:
                errors.extend(error.messages)
        if errors:
            raise ValidationError(errors)
