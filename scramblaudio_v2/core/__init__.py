"""Core engine modules for scramblaudio v2"""

from .sample_bank import SampleBank
from .rhythm import euclidean_rhythm, polymeter_rhythm
from .semantic_space import SemanticSpace
from .arrangement import Section, Arrangement
from .renderer import Renderer
from .effects import EffectsChain, EffectConfig, create_ambient_chain, create_distorted_chain, create_lo_fi_chain, create_clean_chain
from .semantic_automation import SemanticPath, SemanticPathPoint, SemanticAutomation, LFO, PerlinNoiseModulator

__all__ = [
    'SampleBank',
    'euclidean_rhythm',
    'polymeter_rhythm',
    'SemanticSpace',
    'Section',
    'Arrangement',
    'Renderer',
    'EffectsChain',
    'EffectConfig',
    'create_ambient_chain',
    'create_distorted_chain',
    'create_lo_fi_chain',
    'create_clean_chain',
    'SemanticPath',
    'SemanticPathPoint',
    'SemanticAutomation',
    'LFO',
    'PerlinNoiseModulator'
]
