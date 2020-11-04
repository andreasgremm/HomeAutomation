# Lineare Regression mit SKLEARN und PyTorch
Im Rahmen der Home-Automation steht ein Temperatursensor in einem Gehäuse direkt am Fenster.
Durch die Sonneneinstrahlung findet eine zusätzliche Temperaturerhöhung innerhalb des Gehäuses statt. Die vorhandene Gehäuselüftung (passiv durch Öffnungen im Gehäuse) vermag diese jedoch nicht vollständig auszugleichen.

Die Idee ist nun durch eine zweite Messung während eines bestimmten Zeitraums mit einem etwas abgesetzten Temperatursensor, der nicht der direkten Sonneneinstrahlung unterliegt, reale Vergleichswerte zu bekommen.
Diese Messung habe ich mit der **Auto**-Alarmanlage durchgeführt, die während dieser Zeit eben nicht mehr im Auto platziert war und aufgrund der nativen Alarmanlage im Auto auch dort nicht mehr benötigt wird.

Ein Ausschnitt aus dem August zeigt den Effekt sehr anschaulich:

![](screenshots/Bildschirmfoto%202020-11-03%20um%2010.31.58.png)

Über eine Lineare Regression müsste die reale Temperatur vorhersagbar sein.
Diese reale Temperatur ist von den Variablen Helligkeit und gemessene Temperatur abhängig. Dieses sind die unten beschriebenen "X"-Werte, die "y"-Werte sind die gemessenen Temperatur-Vergleichswerte (ohne Sonneneinstrahlung). 

Seit Mai 2020 ist der Vergleichsmechanismus platziert und die Daten sind in die Home-Automation integriert.

Neben den nativen Analogdaten der Sensoren (rechte Achse) sind auch die berechneten Temperaturen (linke Achse) sowie jeweils die 30-minütigen Mittelwerte in der Grafik enthalten.

Um schnelle Ergebnisse zu erhalten, nutze ich als Basis die in den jeweiligen Tutorials angegebene Vorgehensweise und den dort niedergeschriebenen Quellcode.

Die Umgebung wird aufgebaut in dem ein Python-Environment erzeugt wird und die Module aus **Requirements.txt** in diesem Environment installiert werden.

```
python3 -m venv pythonenv
. pythonenv/bin/activate
pip install -r Requirements.txt
```

## Datenextraktion
Über Grafana lassen sich die Daten schnell in CSV-Dateien exportieren.
Vor dem Export muss der Zeitraum für die Dashboards entsprechend eingestellt sein.

Aus dem vorhandenen Grafen:

![](screenshots/Bildschirmfoto%202020-11-02%20um%2018.25.10.png)

Wird jeweils über das Titel-Menu ein CSV-Export angestoßen, um die Temperatur und Helligkeitswerte über verschiedene Zeiträume zu exportieren. (Hier das Beispiel anhand der Temperatur)

![](screenshots/Bildschirmfoto%202020-11-02%20um%2018.26.00.png)

Im folgenden Pop-Up wird dann noch die Achse richtig eingestellt (Series as columns)!

![](screenshots/Bildschirmfoto%202020-11-02%20um%2018.26.23.png)

Die Exportierten Dateien speichern wir mit entsprechenden Namen ab. 

![](screenshots/Bildschirmfoto%202020-11-02%20um%2018.44.38.png)

Ich habe Datensätze für den August, den Oktober und den gesamten Zeitraum der Doppelmessung extrahiert. Die nativen Sensordaten sind nur über den Gesamtzeitraum extrahiert worden.

## Datenaufbereitung
Für die Datenaufbereitung nutze ich das Python Modul [PANDAS](https://pandas.pydata.org/pandas-docs/stable/reference/frame.html).

Die Aufbereitung der Daten besteht im wesentlichen aus wenigen Schritten, die in der Datei **Prepare_light_Temp_Data.py** zusammengefasst sind.

* Einlesen der Temperaturdaten
* Einlesen der Helligkeitsdaten
* Zusammenführen der beiden Datensätze
* Eliminieren der nicht benötigten Spalten (Behalten werden nur die benötigten Mittelwerte) 
* Löschen aller Datensätze, die in den benötigten Spalten ein **NaN** als Zeilenwert enthalten.

In der Datei sind noch ein paar Hilfsfunktionen enthalten, aber die wesentlichen Funktionen sind für die Rückgabe der Trainingsdaten (X- und y- Werte).

Die Nutzung der Datenaufbereitung stellt sich in dem Beispiel folgendermaßen dar:

```
from Prepare_Light_Temp_Data import prepareLightTempData

august = prepareLightTempData(
    "csvs/grafana_Helligkeit_August.csv", "csvs/grafana_Temperatur_August.csv"
)
oktober = prepareLightTempData(
    "csvs/grafana_Helligkeit_Oktober.csv",
    "csvs/grafana_Temperatur_Oktober.csv",
)
komplett = prepareLightTempData(
    "csvs/grafana_Helligkeit.csv", "csvs/grafana_Temperatur.csv"
)
komplett.add_NativeTemp("csvs/grafana_Temperatur-nativ.csv")
```

### Pandas DataFrame 
Ich verwende für das Training und die Validierung der Einfachheit halber die gleichen Datensätze. Über eine [Datums-Selektion](https://stackoverflow.com/questions/29370057/select-dataframe-rows-between-two-dates) könnte auch eine Differenzierung zwischen den Trainings und Validierungsdaten erfolgen.

## Lineare Regression mit SKLEARN
[SKLEARN](https://scikit-learn.org/stable/modules/linear_model.html#multi-task-elastic-net) hat mehrere Regressoren, für dieses Beispiel nutze ich den Multilinearen Regressor, den RANSAC Regressor sowie den Bayesian-Ridge Regressor um Vergleichswerte zu bekommen.

Die Funktionalitäten sind in der Datei **Linear_Analyst.py** in der Klasse ***linearAnalyst*** zusammengefasst.

In der Datei **SKLEARN_Multi_Linear_Regression.py** sind die Codezeilen für die Abfolge enthalten.

Die Regressionen lassen sich auf Basis der Hilfsfunktionen folgendermaßen aufrufen:

```
X = august.get_X()
y = august.get_y()
la1 = linearAnalyst(X, y, "August")
print(la1.predict([[20.947368, 135.000000]]))

X1 = oktober.get_X()
y1 = oktober.get_y()
la2 = linearAnalyst(X1, y1, "Oktober")
print(la2.predict([[20.947368, 135.000000]]))

X2 = komplett.get_X()
y2 = komplett.get_y()
la3 = linearAnalyst(X2, y2, "Komplett")
print(la3.predict([[20.947368, 135.000000]]))

Xn = komplett.get_Xn()
yn = komplett.get_yn()
la4 = linearAnalyst(Xn, yn, "Nativ")

df = linearAnalyst.get_AnalystDataframe()
print(df)
linearAnalyst.write_Excel("test.xlsx")
```

Das Zusatzfeature, die ermittelten Werte in eine Excel-Liste auszugeben, ermöglicht die Übersicht und den Vergleich der Werte:

![](screenshots/Bildschirmfoto%202020-11-02%20um%2019.09.36.png)

Nachfolgend die Darstellung der Ergebnisse für die Lineare Regression mit SKLEARN:

Legende: Blau = gemessene Werte; grün = Vergleichswerte; rot = Vorhersage Werte

**Lineare Regression**:
![](screenshots/Bildschirmfoto%202020-11-04%20um%2014.51.52.png)

**RANSAC Regressor**:
![](screenshots/Bildschirmfoto%202020-11-04%20um%2014.52.50.png)

**Bayesian Ridge Regression**:
![](screenshots/Bildschirmfoto%202020-11-04%20um%2014.53.46.png)

## PyTorch
Auch zu PyTorch gibt es gute [Tutorials](https://pytorch.org/tutorials/beginner/nn_tutorial.html).

Die Nutzung von PyTorch ist komplexer als die Nutzung von SKLEARN und um gute Ergebnisse zu erhalten, benötigt der Anwender mehr Kenntnisse im Bereich Machine-Learning.

Die Datei ***SimpleNet.py*** enthält die zu PyTorch genutzten Hilfsfunktionen.

In der Datei **PYTORCH_Multi_Linear_Regression.py** sind die Codezeilen für die Abfolge enthalten.

Zu den in SKLEARN beschriebenen Datenladefunktionen kommen ein paar spezifische Aufrufe hinzu:

```
X = august.get_X()
y = august.get_y()
X2 = komplett.get_X()
y2 = komplett.get_y()

X_tensor = torch.from_numpy(X.values).float()
y_tensor = torch.from_numpy(y.values).float()
X2_tensor = torch.from_numpy(X2.values).float()

batch_size = 10
train_ds = TensorDataset(X_tensor, y_tensor)
train_dl = DataLoader(train_ds, batch_size, shuffle=True)

valid_ds = TensorDataset(X_tensor, y_tensor)
valid_dl = DataLoader(valid_ds, batch_size=batch_size * 2)

# Define model
model, opt = get_linear_model(2, 1, 1e-5)

# Define loss function
loss_fn = F.mse_loss

# Train the model for 100 epochs
epochs = 100
fit(epochs, model, loss_fn, opt, train_dl, valid_dl)

# Generate predictions
preds = model(X2_tensor)
```
Nachfolgend die Darstellung der Ergebnisse für die Lineare Regression mit PYTORCH:

Legende: Blau = gemessene Werte; grün = Vergleichswerte; rot = Vorhersage Werte

**model = nn.Linear(in\_features, out\_features)**:
![](screenshots/Bildschirmfoto%202020-11-04%20um%2018.35.38.png)

**model = SimpleNet()**:
![](screenshots/Bildschirmfoto%202020-11-04%20um%2018.43.13.png)
