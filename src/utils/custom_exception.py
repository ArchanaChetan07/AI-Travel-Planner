"""
Custom exception with rich diagnostic context.
"""

import sys
import traceback


class TravelPlannerException(Exception):
    """
    Wraps any internal exception and enriches it with:
    - a human-readable message
    - the originating filename and line number
    - the full traceback string (for logs)
    """

    def __init__(self, message: str, original: Exception | None = None) -> None:
        self.original = original
        self.error_message = self._build_message(message, original)
        super().__init__(self.error_message)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _build_message(message: str, original: Exception | None) -> str:
        _, _, exc_tb = sys.exc_info()

        if exc_tb is not None:
            filename = exc_tb.tb_frame.f_code.co_filename
            lineno = exc_tb.tb_lineno
            tb_str = "".join(traceback.format_tb(exc_tb)).strip()
        else:
            filename = "unknown"
            lineno = "unknown"
            tb_str = ""

        parts = [
            f"[TravelPlannerException] {message}",
            f"  Origin  : {filename}:{lineno}",
        ]
        if original:
            parts.append(f"  Cause   : {type(original).__name__}: {original}")
        if tb_str:
            parts.append(f"  Traceback:\n{tb_str}")

        return "\n".join(parts)

    def __str__(self) -> str:
        return self.error_message


# Backwards-compatible alias
CustomException = TravelPlannerException
