"""Implementation of the ``EvaluationContext`` class."""

from __future__ import annotations


class EvaluationContext:
    """The context in which a part of an expression is evaluated.

    TODO: attributes

    """
    # TODO

    # TODO: how do we handle variables?
    # TODO: how do we handle descriptors?
    # TODO: references to prev/next tasks?

    def clone(
        self
    ) -> EvaluationContext:
        """Clone a deep copy of this ``EvaluationContext``."""
        # TODO: this implementation will rely on the design of the class
