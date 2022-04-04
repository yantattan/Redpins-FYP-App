import numpy
import pandas
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split 
from sklearn.metrics import accuracy_score
import joblib


''' inp vars - Data that u have to pass in
    oup vars - The fields that you wish to get your prediction on '''


data = pandas.read_csv("csv/dbcsv/music.csv")
# To predict the value
inp = data.drop(columns=['genre'])
oup = data['genre']

model = DecisionTreeClassifier()
model.fit(inp.values, oup)
print(model.predict([ [21, 1], [30, 0] ]))
# Predict top 3 values
predict_proba = model.predict_proba([21, 1])
best_3 = numpy.argsort(predict_proba, axis=1)[:,-3:]


# Measure accuracy and training sample size
inp = data.drop(columns=['genre'])
oup = data['genre']
inp_train, inp_test, oup_train, oup_test = train_test_split(inp, oup, test_size=0.2)

model = DecisionTreeClassifier()
model.fit(inp_train, oup_train)
predictions = model.predict(inp_test)  # Gives you prediction of the field
print(predictions, accuracy_score(oup_test, predictions)) # accuracy score takes the supposed oup_test against the ones predicted, giving a score of how accurate the algorithm is so far


# Train the model
inp = data.drop(columns=['genre'])
oup = data['genre']

model = DecisionTreeClassifier()
model.fit(inp, oup)

joblib.dump(model, "csv/dbcsv/music-recommender.joblib") # Saves the trained model as a file
newModel = joblib.load("csv/dbcsv/music-recommender.joblib") # Loads the model file in
print(model.predict([ [21, 1], [30, 0] ]))
