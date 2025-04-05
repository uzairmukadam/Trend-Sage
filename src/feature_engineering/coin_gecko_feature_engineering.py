import os
import pandas as pd

class FeatureEngineering:
    def __init__(self, engineered_directory='./src/data/engineered', identifier="gecko"):

        self.identifier = identifier

        os.makedirs(engineered_directory, exist_ok=True)