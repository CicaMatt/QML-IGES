import hashlib
import os
import pathlib
import shutil
import time
import unittest
from os.path import exists

import flask
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy_utils import create_database, database_exists
from src import app, db
from src.source.model.models import User, Dataset


class TestRoutes(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     with app.app_context():
    #         db.session.close_all()
    #         db.drop_all()

    def setUp(self):
        super().setUp()
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "mysql://root@127.0.0.1/test_db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        with app.app_context():
            db.drop_all()
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        with app.app_context():
            db.create_all()

    def test_routes_1(self):
        tester = app.test_client()
        with tester:
            # Setup for login testing
            password = "quercia12345"
            password = hashlib.sha512(password.encode()).hexdigest()
            response = tester.post(
                "/signup",
                data=dict(
                    email="boscoverde27@gmail.com",
                    password=password,
                    confirmPassword=password,
                    username="Antonio",
                    isResearcher="",
                    nome="Antonio",
                    cognome="De Curtis",
                    token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"),
            )

            simpleSplit = True
            scaling = "Standard"
            prototypeSelection = True
            featureExtraction = True
            featureSelection = False
            numRowsPS = 10
            numColsFE = 2
            numColsFS = 2
            model = "SVC"
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"
            backend = "aer_simulator"
            email = "boscoverde27@gmail.com"
            C = 2
            tau = 2
            optimizer = "ADAM"
            loss = "squared_error"
            max_iter = 10
            kernelSVR = "rbf"
            kernelSVC = "rbf"
            C_SVC = 1
            C_SVR = 1

            path = pathlib.Path(__file__).resolve().parent
            pathpred = path / "testingFiles" / "bupaToPredict.csv"
            pathtrain = path / "testingFiles" / "bupa.csv"

            # Test smista with that the whole validation/preprocessing/classification process
            response = tester.post(
                "/formcontrol",
                data=dict(
                    dataset_train=open(pathtrain.__str__(), "rb"),
                    dataset_test=open(pathpred.__str__(), "rb"),
                    dataset_prediction=open(pathpred.__str__(), "rb"),
                    splitDataset=True,
                    scaling=scaling,
                    reducePS=prototypeSelection,
                    reduceFE=featureExtraction,
                    reduceFS=featureSelection,
                    model=model,
                    simpleSplit=simpleSplit,
                    nrRows=numRowsPS,
                    nrColumnsFE=numColsFE,
                    nrColumnsFS=numColsFS,
                    backend=backend,
                    token=token,
                    email=email,
                    Radio="simpleSplit",
                    C=C,
                    tau=tau,
                    optimizer=optimizer,
                    loss=loss,
                    max_iter=max_iter,
                    kernelSVR=kernelSVR,
                    kernelSVC=kernelSVC,
                    C_SVC=C_SVC,
                    C_SVR=C_SVR,
                ),
            )

            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            pathData = pathlib.Path.home() / "QMLdata" / current_user.email / str(
                Dataset.query.filter_by(
                    email_user=current_user.email).order_by(
                    desc(
                        Dataset.id)).first().id)
            self.assertTrue(exists(pathData / "Data_training.dat") or exists(pathData / "Data_training.csv"))
            self.assertTrue(exists(pathData / "Data_testing.dat") or exists(pathData / "Data_testing.csv"))
            self.assertTrue(exists(pathData / "featureDataset.dat") or exists(pathData / "featureDataset.csv"))
            self.assertTrue(exists(pathData / "DataSetTrainPreprocessato.dat") or exists(
                pathData / "DataSetTrainPreprocessato.csv"))
            self.assertTrue(
                exists(pathData / "DataSetTestPreprocessato.dat") or exists(pathData / "DataSetTestPreprocessato.csv"))
            self.assertTrue(
                exists(pathData / "Train_Feature_Extraction.dat") or exists(pathData / "Train_Feature_Extraction.csv"))
            self.assertTrue(
                exists(pathData / "Test_Feature_Extraction.dat") or exists(pathData / "Test_Feature_Extraction.csv"))
            self.assertTrue(exists(pathData / "reducedTrainingPS.dat") or exists(pathData / "reducedTrainingPS.csv"))
            time.sleep(0.5)
            self.assertTrue(exists(pathData / "model.dat") or exists(pathData / "model.sav"))

    def test_routes_2(self):
        tester = app.test_client()
        with tester:
            password = "quercia12345"
            password = hashlib.sha512(password.encode()).hexdigest()
            tester.post(
                "/signup",
                data=dict(
                    email="boscoverde27@gmail.com",
                    password=password,
                    confirmPassword=password,
                    username="Antonio",
                    isResearcher="",
                    nome="Antonio",
                    cognome="De Curtis",
                    token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"),
            )

            simpleSplit = True
            data_imputation = True
            scaling = "MinMax"
            balancing = True
            prototypeSelection = True
            featureExtraction = False
            featureSelection = True

            numRowsPS = 10
            numColsFE = 2
            numColsFS = 2
            model = "SVR"
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"
            backend = "aer_simulator"
            email = "boscoverde27@gmail.com"
            C = 2
            tau = 2
            optimizer = "ADAM"
            loss = "squared_error"
            max_iter = 10
            kernelSVR = "rbf"
            kernelSVC = "rbf"
            C_SVC = 1
            C_SVR = 1

            path = pathlib.Path(__file__).resolve().parent
            pathpred = path / "testingFiles" / "bupaToPredict.csv"
            pathtrain = path / "testingFiles" / "bupa.csv"

            # Test smista with that the whole validation/preprocessing/classification process
            response = tester.post(
                "/formcontrol",
                data=dict(
                    dataset_train=open(pathtrain.__str__(), "rb"),
                    dataset_test=open(pathpred.__str__(), "rb"),
                    dataset_prediction=open(pathpred.__str__(), "rb"),
                    splitDataset=True,
                    reducePS=prototypeSelection,
                    reduceFE=featureExtraction,
                    reduceFS=featureSelection,
                    data_imputation=data_imputation,
                    scaling=scaling,
                    balancing=balancing,
                    model=model,
                    simpleSplit=simpleSplit,
                    nrRows=numRowsPS,
                    nrColumnsFE=numColsFE,
                    nrColumnsFS=numColsFS,
                    backend=backend,
                    token=token,
                    email=email,
                    Radio="simpleSplit",
                    C=C,
                    tau=tau,
                    optimizer=optimizer,
                    loss=loss,
                    max_iter=max_iter,
                    kernelSVR=kernelSVR,
                    kernelSVC=kernelSVC,
                    C_SVC=C_SVC,
                    C_SVR=C_SVR,
                ),
            )

            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            pathData = pathlib.Path.home() / "QMLdata" / current_user.email / str(
                Dataset.query.filter_by(
                    email_user=current_user.email).order_by(
                    desc(
                        Dataset.id)).first().id)
            self.assertTrue(exists(pathData / "Data_training.dat") or exists(pathData / "Data_training.csv"))
            self.assertTrue(exists(pathData / "Data_testing.dat") or exists(pathData / "Data_testing.csv"))
            self.assertTrue(exists(pathData / "featureDataset.dat") or exists(pathData / "featureDataset.csv"))
            self.assertTrue(exists(pathData / "DataSetTrainPreprocessato.dat") or exists(
                pathData / "DataSetTrainPreprocessato.csv"))
            self.assertTrue(
                exists(pathData / "DataSetTestPreprocessato.dat") or exists(pathData / "DataSetTestPreprocessato.csv"))
            self.assertTrue(
                exists(pathData / "Train_Feature_Extraction.dat") or exists(pathData / "Train_Feature_Extraction.csv"))
            self.assertTrue(
                exists(pathData / "Test_Feature_Extraction.dat") or exists(pathData / "Test_Feature_Extraction.csv"))
            self.assertTrue(exists(pathData / "reducedTrainingPS.dat") or exists(pathData / "reducedTrainingPS.csv"))
            time.sleep(0.5)
            self.assertTrue(exists(pathData / "model.dat") or exists(pathData / "model.sav"))


    def test_routes_3(self):
        tester = app.test_client()
        with tester:
            password = "quercia12345"
            password = hashlib.sha512(password.encode()).hexdigest()
            tester.post(
                "/signup",
                data=dict(
                    email="boscoverde27@gmail.com",
                    password=password,
                    confirmPassword=password,
                    username="Antonio",
                    isResearcher="",
                    nome="Antonio",
                    cognome="De Curtis",
                    token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"),
            )

            kFold = True
            kFoldValue = 10
            prototypeSelection = False
            featureExtraction = True
            featureSelection = False
            numColsFE = 2
            model = "None"
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"
            email = "boscoverde27@gmail.com"


            path = pathlib.Path(__file__).resolve().parent
            pathpred = path / "testingFiles" / "bupaToPredict.csv"
            pathtrain = path / "testingFiles" / "bupa.csv"

            # Test smista with that the whole validation/preprocessing/classification process
            response = tester.post(
                "/formcontrol",
                data=dict(
                    dataset_train=open(pathtrain.__str__(), "rb"),
                    dataset_test=open(pathpred.__str__(), "rb"),
                    dataset_prediction=open(pathpred.__str__(), "rb"),
                    reducePS=prototypeSelection,
                    reduceFE=featureExtraction,
                    reduceFS=featureSelection,
                    model=model,
                    kFold=kFold,
                    kFoldValue=kFoldValue,
                    nrColumnsFE=numColsFE,
                    token=token,
                    email=email,
                    Radio="kFold",
                ),
            )

            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            pathData = pathlib.Path.home() / "QMLdata" / current_user.email / str(
                Dataset.query.filter_by(
                    email_user=current_user.email).order_by(
                    desc(
                        Dataset.id)).first().id)
            self.assertTrue(exists(pathData / "training_fold_1.dat") or exists(pathData / "training_fold_1.csv"))
            self.assertTrue(exists(pathData / "training_fold_2.dat") or exists(pathData / "training_fold_2.csv"))
            self.assertTrue(exists(pathData / "training_fold_3.dat") or exists(pathData / "training_fold_3.csv"))
            self.assertTrue(exists(pathData / "training_fold_4.dat") or exists(pathData / "training_fold_4.csv"))
            self.assertTrue(exists(pathData / "training_fold_5.dat") or exists(pathData / "training_fold_5.csv"))
            self.assertTrue(exists(pathData / "training_fold_6.dat") or exists(pathData / "training_fold_6.csv"))
            self.assertTrue(exists(pathData / "training_fold_7.dat") or exists(pathData / "training_fold_7.csv"))
            self.assertTrue(exists(pathData / "training_fold_8.dat") or exists(pathData / "training_fold_8.csv"))
            self.assertTrue(exists(pathData / "training_fold_9.dat") or exists(pathData / "training_fold_9.csv"))
            self.assertTrue(exists(pathData / "training_fold_10.dat") or exists(pathData / "training_fold_10.csv"))


    def tearDown(self):
        thread = flask.g
        thread.join()

        directory = pathlib.Path(__file__).resolve().parents[0]
        allFiles = os.listdir(directory)
        csvFiles = [file for file in allFiles if file.endswith((".csv", ".txt", ".xlsx", ".png"))]
        for file in csvFiles:
            path = os.path.join(directory, file)
            os.remove(path)
        if os.path.exists(directory / "testingFiles" / "model.sav"):
            os.remove(directory / "testingFiles" / "model.sav")
        if os.path.exists(pathlib.Path.home() / "QMLdata" / "boscoverde27@gmail.com"):
            shutil.rmtree(pathlib.Path.home() / "QMLdata" / "boscoverde27@gmail.com")
        with app.app_context():
            db.session.close_all()
            db.drop_all()


    # @classmethod
    # def tearDownClass(cls):
    #     with app.app_context():
    #         db.session.close_all()
    #         db.drop_all()
