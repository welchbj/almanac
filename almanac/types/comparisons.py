from typing import Any, Type

from typing_inspect import get_args, is_union_type


def is_matching_type(_type: Type, annotation: Any) -> bool:
    """Return whether a specified type matches an annotation.

    This function does a bit more than a simple comparison, and performs the following
    extra checks:

        - If the ``annotation`` is a union, then the union is unwrapped and each of
          its types is compared against ``_type``.
        - If the specified ``_type`` is generic, it will verify that all of its
          parameters match those of a matching annotation.

    """
    # Look for an easy win.
    if _type == annotation:
        return True

    # If annotation is Union, we unwrap it to check against each of the possible inner
    # types.
    if is_union_type(annotation):
        if any(_type == tt for tt in get_args(annotation, evaluate=True)):
            return True

    # If both the global type and the argument annotation can be reduced to
    # the same base type, and have equivalent argument tuples, we can
    # assume that they are equivalent.
    # TODO
    return False
