import hashlib
import os
import pathlib
import unittest
import warnings
from src.source.utente.test_UtenteControl import Test_signup, Test_Login_Logout
from src.source.validazioneDataset.test_Validazione import TestValidazioneControl, TestKFold, TestSimpleSplit
from src.source.gestione.test_GestioneControl import TestList, TestUser
from src.source.preprocessingDataset.test_PreprocessingControl import TestPreprocessingControl
from src.source.utils.test_utils import Test_utils
from src.source.testing.test_routes import TestRoutes
from src.source.classificazioneDataset.test_ClassifyControl import TestClassifyControl, TestIbmFail

warnings.filterwarnings("ignore", category=DeprecationWarning)


if __name__ == '__main__':
    unittest.main()






