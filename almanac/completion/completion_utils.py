from typing import Optional, Iterable

from prompt_toolkit.completion import Completion


def rewrite_completion_stream(
    completions: Iterable[Completion],
    *,
    text: Optional[str] = None,
    start_position: Optional[int] = None,
    display_meta: Optional[str] = None,
    style: Optional[str] = None,
    selected_style: Optional[str] = None
) -> Iterable[Completion]:
    """Update field(s) of a stream of completions."""
    for completion in completions:
        new_text = text if text is not None else completion.text
        new_start_position = (
            start_position if start_position is not None else completion.start_position
        )
        new_display_meta = (
            display_meta if display_meta is not None else completion._display_meta
        )
        new_style = style if style is not None else completion.style
        new_selected_style = (
            selected_style if selected_style is not None else completion.selected_style
        )

        yield Completion(
            text=new_text,
            start_position=new_start_position,
            display_meta=new_display_meta,
            style=new_style,
            selected_style=new_selected_style
        )
