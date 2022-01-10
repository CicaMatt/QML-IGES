import os

from app.source.classificazioneDataset import ClassificazioneControl
from app.source.validazioneDataset import kFoldValidation
from app.source.validazioneDataset import train_testSplit
import hashlib
from flask_login import UserMixin, AnonymousUserMixin
import datetime
from unittest import TestCase
from sqlalchemy_utils import database_exists, create_database
from app import db
from app.models import Article
from datetime import datetime
import pathlib
import unittest
from os.path import exists

from flask_login import current_user
from app.models import User
from app import app
from app.source.utils import utils

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestValidazioneControl(unittest.TestCase):
    def setUp(self):
        current_user = User(email="boscoverde27@gmail.com", password="prosopagnosia", username="Antonio de Curtis",
                            name="Antonio", surname="De Curtis",
                            token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2")
        self.assertTrue(current_user.is_authenticated)

    def test_ValidazioneControl_SimpleSplit(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathTest = None
        simpleSplit = True
        kFold = None
        k = 10

        response = tester.post('/validazioneControl',
                               data=dict(userpath=userpath, userpathTest=userpathTest,
                                         simpleSplit=simpleSplit, kFold=kFold, k=k))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        pathData = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathData / "Data_training.csv"))
        self.assertTrue(exists(pathData / "Data_testing.csv"))
        self.assertTrue(exists(pathData / "featureDataset.csv"))

    def test_ValidazioneControl_KFold(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathTest = None
        simpleSplit = None
        kFold = True
        k = 10

        response = tester.post('/validazioneControl',
                               data=dict(userpath=userpath, userpathTest=userpathTest,
                                         simpleSplit=simpleSplit, kFold=kFold, k=k))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        pathData = pathlib.Path(__file__).parents[0]

        for x in range(k):
            StringaTrain = 'training_fold_{}.csv'.format(x + 1)
            StringaTest = 'testing_fold_{}.csv'.format(x + 1)
            self.assertTrue(exists(pathData / StringaTrain))
            self.assertTrue(exists(pathData / StringaTest))

    def test_ValidazioneControl_kFold_Fail(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathTest = None
        simpleSplit = None
        kFold = True
        k = 1

        response = tester.post('/validazioneControl',
                               data=dict(userpath=userpath, userpathTest=userpathTest,
                                         simpleSplit=simpleSplit, kFold=kFold, k=k))
        statuscode = response.status_code
        self.assertEqual(statuscode, 400)
        pathData = pathlib.Path(__file__).parents[0]
        StringaTrain = 'training_fold_1.csv'
        StringaTest = 'testing_fold_1.csv'
        self.assertFalse(exists(pathData / StringaTrain))
        self.assertFalse(exists(pathData / StringaTest))

    def test_ValidazioneControl_KFold_SimpleSplit(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathTest = None
        simpleSplit = True
        kFold = True
        k = 10

        response = tester.post('/validazioneControl',
                               data=dict(userpath=userpath, userpathTest=userpathTest,
                                         simpleSplit=simpleSplit, kFold=kFold, k=k))
        statuscode = response.status_code
        self.assertEqual(statuscode, 400)
        pathData = pathlib.Path(__file__).parents[0]

        for x in range(k):
            StringaTrain = 'training_fold_{}.csv'.format(x + 1)
            StringaTest = 'testing_fold_{}.csv'.format(x + 1)
            self.assertFalse(exists(pathData / StringaTrain))
            self.assertFalse(exists(pathData / StringaTest))

        self.assertFalse(exists(pathData / "Data_training.csv"))
        self.assertFalse(exists(pathData / "Data_testing.csv"))
        self.assertFalse(exists(pathData / "featureDataset.csv"))

    def test_ValidazioneControl_NoSplit(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathTest = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        simpleSplit = None
        kFold = None
        k = 10

        response = tester.post('/validazioneControl',
                               data=dict(userpath=userpath, userpathTest=userpathTest,
                                         simpleSplit=simpleSplit, kFold=kFold, k=k))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        pathData = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathData / "Data_training.csv"))
        self.assertTrue(exists(pathData / "Data_testing.csv"))

    def test_ValidazioneControl_NoSplit_Fail(self):
        tester = app.test_client()
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathTest = None
        simpleSplit = None
        kFold = None
        k = 10

        response = tester.post('/validazioneControl',
                               data=dict(userpath=userpath, userpathTest=userpathTest,
                                         simpleSplit=simpleSplit, kFold=kFold, k=k))
        statuscode = response.status_code
        self.assertEqual(statuscode, 400)
        pathData = pathlib.Path(__file__).parents[0]

        self.assertFalse(exists(pathData / "Data_training.csv"))
        self.assertFalse(exists(pathData / "Data_testing.csv"))

    def tearDown(self):
        directory = pathlib.Path(__file__).parents[0]
        allFiles = os.listdir(directory)
        csvFiles = [file for file in allFiles if file.endswith(".csv")]
        for file in csvFiles:
            path = os.path.join(directory, file)
            os.remove(path)


class TestKFold(unittest.TestCase):

    def test_KFold(self):
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        k = 10

        kFoldValidation.cross_fold_validation(userpath, k)
        pathData = pathlib.Path(__file__).parents[0]

        for x in range(k):
            StringaTrain = 'training_fold_{}.csv'.format(x + 1)
            StringaTest = 'testing_fold_{}.csv'.format(x + 1)
            self.assertTrue(exists(pathData / StringaTrain))
            self.assertTrue(exists(pathData / StringaTest))

    def tearDown(self):
        directory = pathlib.Path(__file__).parents[0]
        allFiles = os.listdir(directory)
        csvFiles = [file for file in allFiles if file.endswith(".csv")]
        for file in csvFiles:
            path = os.path.join(directory, file)
            os.remove(path)


class TestSimpleSplit(unittest.TestCase):

    def test_simpleSplit(self):
        filename = pathlib.Path(__file__).parents[0] / 'testingFiles' / 'bupa.csv'
        numRaws = utils.numberOfRaws(filename.__str__())

        train_testSplit.splitDataset(filename.__str__())
        self.assertEqual(20, utils.numberOfRaws('Data_testing.csv'))
        self.assertEqual(numRaws - 20, utils.numberOfRaws('Data_training.csv'))
        self.assertTrue(exists(pathlib.Path(__file__).parents[0] / "Data_testing.csv"))
        self.assertTrue(exists(pathlib.Path(__file__).parents[0] / "Data_training.csv"))

    def tearDown(self):
        os.remove('Data_testing.csv')
        os.remove('Data_training.csv')


class TestPreprocessingControl(unittest.TestCase):

    def setUp(self):
        current_user = User(email="boscoverde27@gmail.com", password="prosopagnosia", username="Antonio de Curtis",
                            name="Antonio", surname="De Curtis",
                            token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2")
        self.assertTrue(current_user.is_authenticated)

        # path del dataset a disposizione del testing
        pathOrigin = pathlib.Path(__file__).parents[0] / 'testingFiles'
        # path della cartella dell'utente Totò, dove creare i files
        # al momento è la directory del progetto
        pathMock = pathlib.Path(__file__).parents[0]

        f = open((pathMock / 'Data_testing.csv').__str__(), "a+")
        g = open((pathOrigin / 'Data_testing.csv').__str__(), "r")
        contents = g.read()
        f.write(contents)
        f.close()
        g.close()

        f = open((pathMock / 'Data_training.csv').__str__(), "a+")
        g = open((pathOrigin / 'Data_training.csv').__str__(), "r")
        contents = g.read()
        f.write(contents)
        f.close()
        g.close()

        self.assertTrue(exists(pathMock / "Data_training.csv"))
        self.assertTrue(exists(pathMock / "Data_training.csv"))

    def test_PreprocessingControl_onlyQSVM(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupaToPredict.csv"
        prototypeSelection = None
        featureExtraction = None
        numRawsPS = 10
        numColsFE = 2
        doQSVM = True

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        pathMock = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathMock / 'DataSetTrainPreprocessato.csv'))
        self.assertTrue(exists(pathMock / 'DataSetTestPreprocessato.csv'))

    def test_PreprocessingControl_onlyPS(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = None
        prototypeSelection = True
        featureExtraction = None
        numRawsPS = 10
        numColsFE = 2
        doQSVM = None

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        pathMock = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathMock / 'DataSetTrainPreprocessato.csv'))
        self.assertTrue(exists(pathMock / 'DataSetTestPreprocessato.csv'))
        self.assertTrue(exists(pathMock / 'reducedTrainingPS.csv'))

    def test_PreprocessingControl_failPS(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = None
        prototypeSelection = True
        featureExtraction = None
        numRawsPS = 100000
        numColsFE = 2
        doQSVM = None

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 400)

        pathData = pathlib.Path(__file__).parents[0]
        self.assertFalse(exists(pathData / 'DataSetTrainPreprocessato.csv'))
        self.assertFalse(exists(pathData / 'DataSetTestPreprocessato.csv'))
        self.assertFalse(exists(pathData / 'reducedTrainingPS.csv'))

    def test_PreprocessingControl_onlyFE(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = None
        prototypeSelection = None
        featureExtraction = True
        numRawsPS = 10
        numColsFE = 2
        doQSVM = None

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        pathData = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathData / 'DataSetTrainPreprocessato.csv'))
        self.assertTrue(exists(pathData / 'DataSetTestPreprocessato.csv'))
        self.assertTrue(exists(pathData / 'yourPCA_Train.csv'))
        self.assertTrue(exists(pathData / 'yourPCA_Test.csv'))

    def test_PreprocessingControl_failFE(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = None
        prototypeSelection = None
        featureExtraction = True
        numRawsPS = 10
        numColsFE = 15
        doQSVM = None

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 400)

        pathData = pathlib.Path(__file__).parents[0]
        self.assertFalse(exists(pathData / 'DataSetTrainPreprocessato.csv'))
        self.assertFalse(exists(pathData / 'DataSetTestPreprocessato.csv'))
        self.assertFalse(exists(pathData / 'yourPCA_Train.csv'))
        self.assertFalse(exists(pathData / 'yourPCA_Test.csv'))

    def test_PreprocessingControl_FE_PS(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = None
        prototypeSelection = True
        featureExtraction = True
        numRawsPS = 10
        numColsFE = 2
        doQSVM = None

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        pathData = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathData / 'DataSetTrainPreprocessato.csv'))
        self.assertTrue(exists(pathData / 'DataSetTestPreprocessato.csv'))
        self.assertTrue(exists(pathData / 'reducedTrainingPS.csv'))
        self.assertTrue(exists(pathData / 'yourPCA_Train.csv'))
        self.assertTrue(exists(pathData / 'yourPCA_Test.csv'))

    def test_PreprocessingControl_FE_QSVM(self):
        tester = app.test_client(self)
        userpath = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupa.csv"
        userpathToPredict = pathlib.Path(__file__).parents[0] / "testingFiles" / "bupaToPredict.csv"
        prototypeSelection = None
        featureExtraction = True
        numRawsPS = 10
        numColsFE = 2
        doQSVM = True

        response = tester.post("/preprocessingControl",
                               data=dict(userpath=userpath, userpathToPredict=userpathToPredict,
                                         prototypeSelection=prototypeSelection,
                                         featureExtraction=featureExtraction,
                                         numRawsPS=numRawsPS, numColsFE=numColsFE, doQSVM=doQSVM))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        pathData = pathlib.Path(__file__).parents[0]
        self.assertTrue(exists(pathData / 'DataSetTrainPreprocessato.csv'))
        self.assertTrue(exists(pathData / 'DataSetTestPreprocessato.csv'))
        self.assertTrue(exists(pathData / 'yourPCA_Train.csv'))
        self.assertTrue(exists(pathData / 'yourPCA_Test.csv'))
        self.assertTrue(exists(pathData / 'doPredictionFE.csv'))

    def tearDown(self):
        directory = pathlib.Path(__file__).parents[0]
        allFiles = os.listdir(directory)
        csvFiles = [file for file in allFiles if file.endswith(".csv")]
        for file in csvFiles:
            path = os.path.join(directory, file)
            os.remove(path)


class Test_signup(TestCase):

    def setUp(self):
        super().setUp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@127.0.0.1/test_db'
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        with app.app_context():
            db.create_all()

    def test_signup(self):
        """
        test the sign-up functionality of the website, creating a dummy  account and verifying it was correctly
        registered as a user
        """
        tester = app.test_client()
        response = tester.post(
            '/signup',
            data=dict(email="mariorossi12@gmail.com", password="prosopagnosia", username="Antonio de Curtis ",
                      token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2",
                      nome="Antonio", cognome="De Curtis"))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertTrue(User.query.filter_by(email='mariorossi12@gmail.com').first())
        db.session.commit()

    def test_signupEmptyToken(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty and verifying it was
        correctly registered as a user and the token was correctly parsed to Null
        """
        tester = app.test_client()
        response = tester.post(
            '/signup',
            data=dict(email="mariorossi12@gmail.com", password="prosopagnosia", username="Antonio de Curtis ",
                      token="",
                      nome="Antonio", cognome="De Curtis"))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        user = User.query.filter_by(email='mariorossi12@gmail.com').first()
        self.assertTrue(user)
        self.assertIsNone(user.token)
        db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all()


class Test_Login_Logout(TestCase):
    def setUp(self):
        super().setUp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@127.0.0.1/test_db'
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        with app.app_context():
            db.create_all()
            password = 'quercia'
            password = hashlib.sha512(password.encode()).hexdigest()
            utente = User(email="boscoverde27@gmail.com", password=password, username="Antonio de Curtis",
                          name="Antonio", surname="De Curtis")
            db.session.add(utente)
            db.session.commit()

    def test_LoginLogout(self):
        """
        test the login functionality of the website,by trying to log in a predetermined and existing user account and
        then logging out
        """
        tester = app.test_client()
        self.assertFalse(current_user)
        with tester:
            response = tester.post(
                '/login',
                data=dict(email="boscoverde27@gmail.com", password='quercia'))
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            assert isinstance(current_user, User)
            self.assertTrue(current_user.is_authenticated)
            response = tester.post('/logout')
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertFalse(current_user.is_authenticated)

    def test_loginUnregistered(self):
        tester = app.test_client()
        self.assertFalse(current_user)
        with tester:
            response = tester.post(
                '/login',
                data=dict(email="emailsbagliata1234d@gmail.com", password='quercia'))
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertNotIsInstance(current_user, UserMixin)
            self.assertIsInstance(current_user, AnonymousUserMixin)
            self.assertFalse(current_user.is_authenticated)

    def test_loginWrongPassword(self):
        tester = app.test_client()
        self.assertFalse(current_user)
        with tester:
            response = tester.post(
                '/login',
                data=dict(email="boscoverde27@gmail.com", password='passwordsbagliata'))
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertNotIsInstance(current_user, UserMixin)
            self.assertIsInstance(current_user, AnonymousUserMixin)
            self.assertFalse(current_user.is_authenticated)

    def test_Newsletter(self):
        tester = app.test_client()
        with tester:
            tester.post(
                '/login',
                data=dict(email="boscoverde27@gmail.com", password='quercia'))
            assert isinstance(current_user, User)
            self.assertFalse(current_user.newsletter)
            response = tester.post(
                '/newsletter',
                data=dict(email="boscoverde27@gmail.com"))
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertTrue(current_user.newsletter)

    def tearDown(self):
        with app.app_context():
            db.drop_all()


class TestUser(TestCase):

    def setUp(self):
        super().setUp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@127.0.0.1/test_db'
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        tester = app.test_client(self)
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        with app.app_context():
            db.create_all()
            user = User(email="mariorossi12@gmail.com", password="prosopagnosia", username="Antonio de Curtis ",
                        name="Antonio", surname="De Curtis")
            db.session.add(user)
            db.session.commit()

    def test_removeUser(self):
        tester = app.test_client(self)
        with app.app_context():
            db.create_all()
            self.assertTrue(User.query.filter_by(email='mariorossi12@gmail.com').first())
            response = tester.post(
                '/removeUser/',
                data=dict(email="mariorossi12@gmail.com"))
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertFalse(User.query.filter_by(email="mariorossi12@gmail.com").first())
            db.session.commit()

    def test_modifyUser(self):
        tester = app.test_client()
        with app.app_context():
            db.create_all()
        self.assertTrue(User.query.filter_by(email='mariorossi12@gmail.com').first())
        response = tester.post(
            '/ModifyUser/',
            data=dict(email="mariorossi12@gmail.com", password="newPassword", username="newUsername ",
                      nome="newName", cognome="newSurname"))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertTrue(User.query.filter_by(email='mariorossi12@gmail.com', username='newUsername').first())
        db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all();


class TestList(TestCase):
    def setUp(self):
        super().setUp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@127.0.0.1/test_db'
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        tester = app.test_client(self)
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        with app.app_context():
            db.create_all()
            user1 = User(email="mariorossi12@gmail.com", password="prosopagnosia", username="Antonio de Curtis ",
                         name="Antonio", surname="De Curtis")
            user2 = User(email="giuseppeverdi@gmail.com", password="asperger", username="giuVerdiProXX",
                         name="Giuseppe", surname="Verdi")
            art1 = Article(email_user="mariorossi12@gmail.com", title="BuonNatale", body="primobody",
                           category="primaCat", data=datetime(2021, 12, 25))
            art2 = Article(email_user="mariorossi12@gmail.com", title="BuonCapodanno", body="secondoBody",
                           category="secondaCat", data=datetime(2022, 1, 1))
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            db.session.add(art1)
            db.session.add(art2)
            db.session.commit()

    def test_listUser(self):
        tester = app.test_client()
        with app.app_context():
            db.create_all()
        self.assertTrue(User.query.filter_by(email='mariorossi12@gmail.com').first())
        response = tester.post(
            '/gestione/',
            data=dict(scelta="listUser", email="mariorossi12@gmail.com"))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertTrue(User.query.filter_by(email='mariorossi12@gmail.com').first())
        self.assertTrue(User.query.filter_by(email='giuseppeverdi@gmail.com').first())
        db.session.commit()

    def test_listArticlesUser(self):
        tester = app.test_client()
        with app.app_context():
            db.create_all()
        response = tester.post(
            '/gestione/',
            data=dict(scelta="listArticlesUser", email="mariorossi12@gmail.com"))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertTrue(Article.query.filter_by(email_user='mariorossi12@gmail.com').limit(2))
        db.session.commit()

    def test_listArticlesData(self):
        tester = app.test_client()
        with app.app_context():
            db.create_all()
        response = tester.post(
            '/gestione/',
            data=dict(scelta="listArticlesData", firstData='2021-12-20', secondData='2021-12-30'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertTrue(Article.query.filter(Article.data.between('2021-12-20', '2021-12-30')).first())
        db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all();

class TestClassificazioneControl(unittest.TestCase):
    def setUp(self):
       current_user = User(email="boscoverde27@gmail.com", password="prosopagnosia", username="Antonio de Curtis",
                         name="Antonio", surname="De Curtis", token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2")
       self.assertTrue(current_user.is_authenticated)


    def test_ClassificazioneControl(self):
        tester = app.test_client(self)
        pathTrain = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTrainPreprocessato.csv"
        pathTest = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTestPreprocessato.csv"
        pathPrediction = pathlib.Path(__file__).cwd() / "testingFiles" / "doPrediction.csv"
        features = utils.createFeatureList(2)
        token = '43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2'
        backend = "ibmq_qasm_simulator"

        response = tester.post(
            '/classificazioneControl',
            data=dict(pathTrain=pathTrain, pathTest=pathTest,
                      pathPrediction=pathPrediction, features=features,
                      token=token, backend=backend))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertTrue(exists(pathlib.Path(__file__).parents[3] / "upload_dataset" / "classifiedFile.csv"))


    def test_classify(self):
        pathTrain = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTrainPreprocessato.csv"
        pathTest = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTestPreprocessato.csv"
        pathPrediction = pathlib.Path(__file__).cwd() / "testingFiles" / "doPrediction.csv"
        features = utils.createFeatureList(2)
        token = '43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2'
        backendSelected = "ibmq_qasm_simulator"

        result = ClassificazioneControl.classify(pathTrain, pathTest, pathPrediction, features, token, backendSelected)
        self.assertNotEqual(result, 0)
        self.assertNotEqual(result, 1)
        self.assertTrue(exists(pathlib.Path(__file__).parents[3] / "upload_dataset" / "classifiedFile.csv"))


    def test_classify_tokenFail(self):
        pathTrain = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTrainPreprocessato.csv"
        pathTest = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTestPreprocessato.csv"
        pathPrediction = pathlib.Path(__file__).cwd() / "testingFiles" / "doPrediction.csv"
        features = utils.createFeatureList(2)
        token = 't0kenN0tV4l1d'
        backendSelected = "ibmq_qasm_simulator"

        result = ClassificazioneControl.classify(pathTrain, pathTest, pathPrediction, features, token, backendSelected)
        self.assertEqual(result, 0)
        self.assertNotEqual(result, 1)


    def test_classify_ibmFail(self):
        pathTrain = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTrainPreprocessato.csv"
        pathTest = pathlib.Path(__file__).cwd() / "testingFiles" / "DataSetTestPreprocessato.csv"
        pathPrediction = pathlib.Path(__file__).cwd() / "testingFiles" / "bupa.csv"
        features = utils.createFeatureList(2)
        token = '43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2'
        backendSelected = "ibmq_qasm_simulator"

        result = ClassificazioneControl.classify(pathTrain, pathTest, pathPrediction, features, token, backendSelected)
        self.assertEqual(result, 1)
        self.assertNotEqual(result, 0)
        self.assertFalse(exists(pathlib.Path(__file__).parents[3] / "upload_dataset" / "classifiedFile.csv"))


    def test_getClassifiedDataset(self):
        result={}
        result["testing_accuracy"]=0.55687446747
        result["test_success_ratio"] =0.4765984595
        result["totalTime"]=str(90.7)
        classifiedFile=open( pathlib.Path(__file__).parents[3] / "upload_dataset" / "classifiedFile.csv", "w")

        value = ClassificazioneControl.getClassifiedDataset(result)
        classifiedFile.close()
        self.assertEqual(value, 1)

    def tearDown(self):
        if(os.path.exists(pathlib.Path(__file__).parents[3] / "upload_dataset" / "classifiedFile.csv")):
            os.remove(pathlib.Path(__file__).parents[3] / "upload_dataset" / "classifiedFile.csv")








