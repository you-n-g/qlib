"""
Interfaces to interpret models
"""

import pandas as pd
from abc import abstractmethod


class FeatureInt:
    """Feature (Int)erpreter"""
    @abstractmethod
    def get_feature_importance(self) -> pd.Series:
        ...
