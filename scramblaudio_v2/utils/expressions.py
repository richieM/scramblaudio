"""
Expression Parser - Parse human-readable expressions for semantic navigation

Allows you to write things like:
    "bright->dark over 4 bars"
    "orbit(kick_1, radius=2.0, 16 bars)"
    "random_walk(snare_5, chaos=0.8, 32 beats)"
"""

import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ParsedExpression:
    """Parsed semantic navigation expression"""
    command: str  # 'sweep', 'orbit', 'walk', 'gradient'
    start_sample: Optional[str] = None
    end_sample: Optional[str] = None
    feature: Optional[str] = None
    amount: float = 1.0
    duration: float = 4.0
    duration_unit: str = 'bars'  # 'bars', 'beats', 'seconds'
    radius: float = 1.0
    step_size: float = 0.5
    revolutions: float = 1.0
    num_steps: int = 10


class ExpressionParser:
    """
    Parse semantic navigation expressions

    Examples:
        "bright->dark over 4 bars" → gradient sweep
        "kick_1->kick_5 over 8 beats" → linear sweep
        "orbit(center=kick_3, radius=2, 16 bars)" → orbit
        "walk(start=snare_1, chaos=0.8, 32 beats)" → random walk
        "gradient(start=hat_1, feature=brightness, amount=3, 4 bars)" → feature gradient
    """

    # Regex patterns
    SWEEP_PATTERN = r"(\w+)->(\w+)\s+over\s+([\d.]+)\s+(bars|beats|seconds)"
    ORBIT_PATTERN = r"orbit\((.+?)\)"
    WALK_PATTERN = r"walk\((.+?)\)"
    GRADIENT_PATTERN = r"gradient\((.+?)\)"

    def __init__(self):
        """Initialize parser"""
        pass

    def parse(self, expression: str) -> Optional[ParsedExpression]:
        """
        Parse an expression string

        Args:
            expression: Expression to parse

        Returns:
            ParsedExpression or None if parsing failed
        """
        expression = expression.strip().lower()

        # Try sweep pattern (A->B)
        match = re.match(self.SWEEP_PATTERN, expression)
        if match:
            return self._parse_sweep(match)

        # Try orbit pattern
        match = re.match(self.ORBIT_PATTERN, expression)
        if match:
            return self._parse_orbit(match)

        # Try walk pattern
        match = re.match(self.WALK_PATTERN, expression)
        if match:
            return self._parse_walk(match)

        # Try gradient pattern
        match = re.match(self.GRADIENT_PATTERN, expression)
        if match:
            return self._parse_gradient(match)

        # Failed to parse
        print(f"Warning: Could not parse expression: {expression}")
        return None

    def _parse_sweep(self, match: re.Match) -> ParsedExpression:
        """Parse sweep expression (A->B)"""
        start, end, duration, unit = match.groups()

        return ParsedExpression(
            command='sweep',
            start_sample=start,
            end_sample=end,
            duration=float(duration),
            duration_unit=unit
        )

    def _parse_orbit(self, match: re.Match) -> ParsedExpression:
        """Parse orbit expression"""
        args_str = match.group(1)
        args = self._parse_args(args_str)

        expr = ParsedExpression(command='orbit')

        # Extract parameters
        if 'center' in args:
            expr.start_sample = args['center']
        if 'start' in args:
            expr.start_sample = args['start']
        if 'radius' in args:
            expr.radius = float(args['radius'])
        if 'revolutions' in args:
            expr.revolutions = float(args['revolutions'])

        # Duration (last positional arg)
        duration_match = re.search(r'([\d.]+)\s+(bars|beats|seconds)', args_str)
        if duration_match:
            expr.duration = float(duration_match.group(1))
            expr.duration_unit = duration_match.group(2)

        return expr

    def _parse_walk(self, match: re.Match) -> ParsedExpression:
        """Parse random walk expression"""
        args_str = match.group(1)
        args = self._parse_args(args_str)

        expr = ParsedExpression(command='walk')

        # Extract parameters
        if 'start' in args:
            expr.start_sample = args['start']
        if 'chaos' in args:
            expr.step_size = float(args['chaos'])
        if 'step_size' in args:
            expr.step_size = float(args['step_size'])
        if 'steps' in args:
            expr.num_steps = int(args['steps'])

        # Duration
        duration_match = re.search(r'([\d.]+)\s+(bars|beats|seconds)', args_str)
        if duration_match:
            expr.duration = float(duration_match.group(1))
            expr.duration_unit = duration_match.group(2)

        return expr

    def _parse_gradient(self, match: re.Match) -> ParsedExpression:
        """Parse gradient expression"""
        args_str = match.group(1)
        args = self._parse_args(args_str)

        expr = ParsedExpression(command='gradient')

        # Extract parameters
        if 'start' in args:
            expr.start_sample = args['start']
        if 'feature' in args:
            expr.feature = args['feature']
        if 'amount' in args:
            expr.amount = float(args['amount'])
        if 'steps' in args:
            expr.num_steps = int(args['steps'])

        # Duration
        duration_match = re.search(r'([\d.]+)\s+(bars|beats|seconds)', args_str)
        if duration_match:
            expr.duration = float(duration_match.group(1))
            expr.duration_unit = duration_match.group(2)

        return expr

    def _parse_args(self, args_str: str) -> Dict[str, str]:
        """Parse key=value arguments"""
        args = {}
        # Match key=value pairs
        for match in re.finditer(r'(\w+)=([\w.]+)', args_str):
            key, value = match.groups()
            args[key] = value
        return args


def convert_duration(duration: float, unit: str, bpm: float = 120.0,
                    time_signature: tuple = (4, 4)) -> float:
    """
    Convert duration from bars/beats/seconds to seconds

    Args:
        duration: Duration value
        unit: 'bars', 'beats', or 'seconds'
        bpm: Tempo in beats per minute
        time_signature: Time signature tuple (numerator, denominator)

    Returns:
        Duration in seconds
    """
    if unit == 'seconds':
        return duration

    beats_per_minute = bpm
    seconds_per_beat = 60.0 / beats_per_minute

    if unit == 'beats':
        return duration * seconds_per_beat
    elif unit == 'bars':
        beats_per_bar = time_signature[0]
        return duration * beats_per_bar * seconds_per_beat
    else:
        raise ValueError(f"Unknown duration unit: {unit}")


# Example usage and tests
if __name__ == "__main__":
    parser = ExpressionParser()

    test_expressions = [
        "kick_1->kick_5 over 4 bars",
        "bright->dark over 8 beats",
        "orbit(center=snare_3, radius=2.0, 16 bars)",
        "walk(start=hat_1, chaos=0.8, 32 beats)",
        "gradient(start=kick_1, feature=brightness, amount=3.0, 4 bars)",
    ]

    print("Expression Parser Tests\n" + "="*50)

    for expr_str in test_expressions:
        print(f"\nInput:  {expr_str}")
        parsed = parser.parse(expr_str)
        if parsed:
            print(f"Command: {parsed.command}")
            print(f"Start:   {parsed.start_sample}")
            print(f"End:     {parsed.end_sample}")
            print(f"Feature: {parsed.feature}")
            print(f"Duration: {parsed.duration} {parsed.duration_unit}")
            print(f"Amount:  {parsed.amount}")
            print(f"Radius:  {parsed.radius}")

    # Test duration conversion
    print("\n" + "="*50)
    print("Duration Conversions (120 BPM, 4/4)")
    print("4 bars =", convert_duration(4, 'bars', bpm=120), "seconds")
    print("16 beats =", convert_duration(16, 'beats', bpm=120), "seconds")
    print("5 seconds =", convert_duration(5, 'seconds', bpm=120), "seconds")
