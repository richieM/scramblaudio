"""
Arrangement module - Song structure and section management

Enables defining song structure (intro, verse, chorus, etc.) with
different instruments, rhythms, and semantic regions per section.
"""

from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field


@dataclass
class Section:
    """
    Represents a section of a song (verse, chorus, etc.)

    Attributes:
        name: Section name (e.g., 'intro', 'verse_a', 'chorus')
        bars: Duration in bars
        bpm: Tempo in beats per minute
        time_signature: Tuple of (numerator, denominator) e.g., (7, 8)
        instruments: Which instrument tracks are active
                    Can be list of names or 'all'
        rhythm_params: Dict of rhythm parameters per instrument
        semantic_params: Dict of semantic space parameters per instrument
        metadata: Additional custom parameters
    """

    name: str
    bars: int
    bpm: float = 120.0
    time_signature: tuple = (4, 4)
    instruments: Union[List[str], str] = 'all'
    rhythm_params: Dict[str, Dict] = field(default_factory=dict)
    semantic_params: Dict[str, Dict] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def duration_seconds(self) -> float:
        """Calculate section duration in seconds"""
        beats_per_bar = self.time_signature[0]
        total_beats = self.bars * beats_per_bar
        return (total_beats / self.bpm) * 60.0

    def __repr__(self):
        return (f"Section('{self.name}', {self.bars} bars, "
                f"{self.time_signature[0]}/{self.time_signature[1]}, "
                f"{self.bpm} bpm)")


class Arrangement:
    """
    Manages song arrangement - sequence of sections

    Provides methods to build, query, and modify song structure.
    """

    def __init__(self, sections: Optional[List[Section]] = None,
                 global_bpm: float = 120.0):
        """
        Initialize arrangement

        Args:
            sections: List of Section objects
            global_bpm: Default BPM for sections that don't specify one
        """
        self.sections = sections or []
        self.global_bpm = global_bpm

    def add_section(self, section: Section):
        """Add a section to the arrangement"""
        self.sections.append(section)

    def add_sections(self, sections: List[Section]):
        """Add multiple sections"""
        self.sections.extend(sections)

    def get_section(self, index: int) -> Optional[Section]:
        """Get section by index"""
        if 0 <= index < len(self.sections):
            return self.sections[index]
        return None

    def get_sections_by_name(self, name: str) -> List[Section]:
        """Get all sections with a given name"""
        return [s for s in self.sections if s.name == name]

    def total_bars(self) -> int:
        """Calculate total number of bars in arrangement"""
        return sum(s.bars for s in self.sections)

    def total_duration(self) -> float:
        """Calculate total duration in seconds"""
        return sum(s.duration_seconds() for s in self.sections)

    def get_timeline(self) -> List[Dict[str, Any]]:
        """
        Get timeline with start/end times for each section

        Returns:
            List of dicts with section info and timing
        """
        timeline = []
        current_time = 0.0

        for section in self.sections:
            duration = section.duration_seconds()

            timeline.append({
                'section': section,
                'start_time': current_time,
                'end_time': current_time + duration,
                'duration': duration
            })

            current_time += duration

        return timeline

    def get_active_instruments(self, section_index: int) -> List[str]:
        """
        Get list of active instruments for a section

        Args:
            section_index: Index of section

        Returns:
            List of instrument names active in that section
        """
        section = self.get_section(section_index)
        if not section:
            return []

        if section.instruments == 'all':
            # Collect all instrument names from all sections
            all_instruments = set()
            for s in self.sections:
                if isinstance(s.instruments, list):
                    all_instruments.update(s.instruments)
            return sorted(list(all_instruments))

        return section.instruments if isinstance(section.instruments, list) else []

    def visualize(self) -> str:
        """
        Create a text visualization of the arrangement

        Returns:
            String representation of the arrangement structure
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"Arrangement: {len(self.sections)} sections, "
                    f"{self.total_bars()} bars, "
                    f"{self.total_duration():.1f}s")
        lines.append("=" * 60)

        timeline = self.get_timeline()

        for i, entry in enumerate(timeline):
            section = entry['section']
            start = entry['start_time']
            end = entry['end_time']

            # Format instruments
            if section.instruments == 'all':
                instr_str = "ALL"
            elif isinstance(section.instruments, list):
                instr_str = ", ".join(section.instruments)
            else:
                instr_str = str(section.instruments)

            lines.append(
                f"{i+1:2d}. {section.name:15s} | "
                f"{section.bars:2d} bars | "
                f"{section.time_signature[0]}/{section.time_signature[1]} | "
                f"{section.bpm:3.0f} bpm | "
                f"[{start:6.1f}s - {end:6.1f}s] | "
                f"{instr_str}"
            )

        lines.append("=" * 60)

        return "\n".join(lines)

    def __repr__(self):
        return (f"Arrangement({len(self.sections)} sections, "
                f"{self.total_bars()} bars, {self.total_duration():.1f}s)")


def create_simple_arrangement(structure: List[tuple],
                              bpm: float = 120.0) -> Arrangement:
    """
    Utility to quickly create an arrangement from a simple structure

    Args:
        structure: List of (name, bars) or (name, bars, instruments) tuples
        bpm: Global BPM

    Returns:
        Arrangement object

    Example:
        >>> arr = create_simple_arrangement([
        ...     ('intro', 4, ['kick', 'perc']),
        ...     ('verse', 8, ['kick', 'snare', 'hihat']),
        ...     ('chorus', 8, 'all')
        ... ], bpm=140)
    """
    sections = []

    for item in structure:
        if len(item) == 2:
            name, bars = item
            instruments = 'all'
        else:
            name, bars, instruments = item

        section = Section(
            name=name,
            bars=bars,
            bpm=bpm,
            instruments=instruments
        )
        sections.append(section)

    return Arrangement(sections, global_bpm=bpm)


if __name__ == "__main__":
    # Example usage
    print("=== Simple Arrangement Example ===\n")

    arr = create_simple_arrangement([
        ('intro', 4, ['kick']),
        ('verse_a', 8, ['kick', 'snare', 'hihat']),
        ('chorus', 8, 'all'),
        ('verse_b', 8, ['kick', 'snare', 'hihat']),
        ('chorus', 8, 'all'),
        ('outro', 4, ['perc'])
    ], bpm=140)

    print(arr.visualize())

    print("\n=== Complex Arrangement with Polymeter ===\n")

    # More complex example with different time signatures
    sections = [
        Section('intro', bars=4, bpm=120, time_signature=(4, 4),
               instruments=['kick']),

        Section('verse', bars=8, bpm=120, time_signature=(7, 8),
               instruments=['kick', 'snare', 'hihat'],
               rhythm_params={
                   'kick': {'hits': 3, 'steps': 7},
                   'snare': {'hits': 5, 'steps': 13},
                   'hihat': {'hits': 7, 'steps': 16}
               }),

        Section('chorus', bars=8, bpm=140, time_signature=(4, 4),
               instruments='all',
               semantic_params={
                   'bass': {'brightness': 0.3, 'noisiness': 0.2},
                   'lead': {'brightness': 0.8, 'noisiness': 0.5}
               })
    ]

    arr2 = Arrangement(sections)
    print(arr2.visualize())
