---
title: "Energiezähler nach falscher Registerreihenfolge korrigieren"
---

# Energiezähler nach falscher Registerreihenfolge korrigieren

*Zuletzt geändert am 27.11.2026*

Die Lambda speichert ihre Energiezähler als 32-Bit-Werte in zwei Registern. In welcher Reihenfolge die beiden Register gelesen werden, legt die Option [32-Bit-Registerreihenfolge](optionen-config-flow.md#32-bit-registerreihenfolge) fest. Ist sie falsch eingestellt, oder war sie es früher einmal, können die Energiezähler der Integration stark überhöhte Werte enthalten.

Diese Seite erklärt, wie Sie das erkennen, die Einstellung korrigieren und die Zähler bereinigen.

## Warum die Werte so groß werden

Die Integration zählt nicht den Rohwert, sondern bei jeder Abfrage nur, um wie viel der Zähler gestiegen ist. Mit vertauschten Registern steigt der gelesene Wert bei jeder Kilowattstunde nicht um 1 kWh, sondern in Stufen von rund **65,5 kWh**. Diese Stufen bleiben unter der Schutzgrenze pro Abfrage und werden mitgezählt. Über Wochen und Monate entstehen so Werte, die eine Wärmepumpe nie erreichen kann, etwa mehrere Hunderttausend oder Millionen kWh im Jahr.

Betroffen sind die Energiezähler der Integration, also die Sensoren mit `_energy_` und `_thermal_energy_` im Namen (Gesamt, Jahr, Monat, Tag), für Heizen, Warmwasser, Kühlen, Abtauen und Standby.

## 1. Erkennen

Eines dieser Zeichen reicht:

- **Unplausible Größenordnung:** Ein Jahres- oder Gesamtzähler zeigt Werte, die weit über dem liegen, was die Wärmepumpe verbrauchen oder abgeben kann. Zum Vergleich: Eine Wärmepumpe im Einfamilienhaus verbraucht im Jahr typischerweise wenige Tausend kWh Strom.
- **Sprünge im Verlauf:** Im Verlauf eines Energiezählers steigt der Wert in Stufen von etwa 65,5 kWh statt gleichmäßig.
- **Reparaturmeldung:** Unter *Einstellungen → System → Reparaturen* steht „32-Bit-Registerreihenfolge von … prüfen“. Diese Meldung erscheint nur bei besonders großen Werten (über 1 GWh). Fehlt sie, kann die Reihenfolge trotzdem falsch sein.
- **Vergleich mit dem Display:** Der Sensor *Verdichter Energie Gesamt* (`…_compressor_power_consumption_accumulated`, in Wh) geteilt durch 1000 sollte ungefähr dem Stromverbrauch entsprechen, den das Display der Lambda anzeigt. Weicht er völlig ab, ist die Reihenfolge falsch.

## 2. Reihenfolge korrigieren

1. *Einstellungen → Geräte & Dienste → Lambda → Konfigurieren*.
2. Die **32-Bit-Registerreihenfolge** auf den anderen Wert stellen (`high_first` oder `low_first`).
3. Absenden. Die Integration lädt neu.
4. Den Sensor *Verdichter Energie Gesamt* erneut mit dem Display vergleichen. Stimmen die Werte jetzt ungefähr überein, ist die Reihenfolge richtig.

Ab jetzt zählt die Integration richtig. Die bereits gezählten, überhöhten Werte bleiben aber in den Zählern stehen. Sie korrigieren Sie in den nächsten Schritten.

## 3. Gesamtzähler mit einem Offset korrigieren

Die Gesamtzähler (`…_energy_total`, `…_thermal_energy_total`) lassen sich mit einem negativen Offset in der Datei `lambda_wp_config.yaml` korrigieren. Wie Offsets grundsätzlich funktionieren, steht unter [Offsets](offsets.md).

**Schritt 1: Den richtigen Wert bestimmen**

Für jeden betroffenen Gesamtzähler:

1. Den Verlauf des Sensors öffnen (Klick auf den Sensor → Verlauf, Zeitraum großzügig wählen).
2. Den **letzten plausiblen Wert** vor den ersten Sprüngen ablesen. Das ist der Stand, bevor die falsche Reihenfolge mitgezählt hat.
3. Wenn Sie den echten Zuwachs seit diesem Zeitpunkt kennen (etwa aus einem eigenen Zähler), addieren Sie ihn. Sonst bleibt dieser Zeitraum als Lücke, die Werte danach sind wieder richtig.

**Schritt 2: Den Offset berechnen**

> **Offset = richtiger Wert − aktuell angezeigter Wert**

Das Ergebnis ist negativ. Beispiel: Der Zähler zeigt 1.358.226 kWh, der letzte plausible Wert war 1.850 kWh. Der Offset ist 1.850 − 1.358.226 = −1.356.376 kWh.

**Schritt 3: In die Datei eintragen**

In `/config/lambda_wp_config.yaml`, Werte in **kWh**:

```yaml
energy_consumption_offsets:
  hp1:
    hot_water_energy_total: -1356376.0
    cooling_energy_total: -12345.0
    hot_water_thermal_energy_total: -98765.0
```

Nur die Zähler eintragen, die tatsächlich falsch sind.

**Schritt 4: Integration neu laden und prüfen**

*Einstellungen → Geräte & Dienste → Lambda → ⋮ → Neu laden.* Danach die Gesamtzähler prüfen. Ein Offset wird nur einmal angewendet, auch nach weiteren Neustarts.

## 4. Tages-, Monats- und Jahreszähler

Für die Zähler über einen Zeitraum gibt es keinen Offset. Sie beginnen zum nächsten Wechsel ihres Zeitraums wieder bei null:

- Tageszähler um Mitternacht,
- Monatszähler zum Monatsersten,
- Jahreszähler erst zum **1. Januar**.

Bis dahin zeigen sie den überhöhten Wert weiter an. Wer das nicht abwarten will, kann die Sensoren ignorieren, bis der Zeitraum gewechselt hat.

## 5. Energie-Dashboard und Langzeitstatistik

Home Assistant speichert für die Energiezähler eine Langzeitstatistik, die auch das Energie-Dashboard nutzt. Die überhöhten Sprünge stehen dort weiterhin, auch nachdem der Zähler korrigiert ist. Die Korrektur per Offset erzeugt dort außerdem einen einmaligen Sprung nach unten.

Beides lässt sich in Home Assistant unter *Entwicklerwerkzeuge → Statistiken* korrigieren: den betroffenen Sensor auswählen und die Summe zum Zeitpunkt des Sprungs anpassen.

## Verwandte Seiten

- [Optionen des Config Flow: 32-Bit-Registerreihenfolge](optionen-config-flow.md#32-bit-registerreihenfolge)
- [Offsets – Historische Daten übernehmen](offsets.md)
- [Falsche / keine Sensorwerte](../FAQ/falsche-keine-sensorwerte.md)
