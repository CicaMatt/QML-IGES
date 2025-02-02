import csv
import math
import os
import time
import pandas as pd
from qiskit.circuit.library import ZFeatureMap
from qiskit.utils import algorithm_globals, QuantumInstance
from qiskit_machine_learning.algorithms import PegasosQSVC, QSVC, QSVR
from qiskit_machine_learning.kernels import QuantumKernel
from sklearn.metrics import precision_score, recall_score, accuracy_score, mean_squared_error, mean_absolute_error
import numpy as np

from src.source.utils import utils
from src.source.utils.utils import createFeatureList, numberOfColumns


class myQSVR:
    def classify(pathTrain, pathTest, path_predict, backend, num_qubits):

        print(pathTrain, pathTest, path_predict)
        data_train = pd.read_csv(pathTrain)
        data_train = data_train.drop(columns='Id') #QSVM richiede l'id e Pegasos no
        train_features = data_train.drop(columns='labels')
        train_labels = data_train["labels"].values
        data_test = pd.read_csv(pathTest)
        data_test = data_test.drop(columns='Id')
        test_features = data_test.drop(columns='labels')
        test_labels = data_test["labels"].values

        prediction_data = np.genfromtxt(path_predict, delimiter=',')

        test_features = test_features.to_numpy() #Pegasos.fit accetta numpy array e non dataframe
        train_features = train_features.to_numpy()

        result = {}
        algorithm_globals.random_seed = 12345

        feature_map = ZFeatureMap(feature_dimension=num_qubits, reps=1)
        qkernel = QuantumKernel(feature_map=feature_map, quantum_instance=QuantumInstance(backend))
        qsvr = QSVR(quantum_kernel=qkernel)

        try:
            # training
            print("Running...")
            start_time = time.time()
            qsvr.fit(train_features, train_labels)
            training_time = time.time() - start_time
            print("Train effettuato in " + str(training_time))

            # test
            start_time = time.time()
            score = qsvr.score(test_features, test_labels)
            test_prediction = qsvr.predict(test_features)
            print(test_labels, test_prediction)
            testing_time = time.time() - start_time
            result["regression_score"] = score
            mse = mean_squared_error(test_labels, test_prediction)
            mae = mean_absolute_error(test_labels, test_prediction)
            result["mse"] = mse
            result["mae"] = mae
            rmse = math.sqrt(mse)
            result["regression_score"] = score
            result["rmse"] = rmse
            result["trained_model"] = qsvr

            # prediction
            start_time = time.time()
            if utils.numberOfColumns(path_predict) == 1:
                prediction_data = prediction_data.reshape(-1, 1)
            if utils.numberOfRows(path_predict) == 1:
                prediction_data = prediction_data.reshape(1, -1)
            predicted_labels = qsvr.predict(prediction_data)
            print(predicted_labels)
            total_time = time.time() - start_time
            print("Prediction effettuata in " + str(total_time))
            result["predicted_labels"] = np.array(predicted_labels)

            result["total_time"] = str(testing_time + training_time)[0:6]
            result["training_time"] = str(training_time)[0:6]
        except Exception as e:
            print(e)
            result["error"] = 1
            result["exception"] = e
        return result
