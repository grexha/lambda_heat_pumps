---
title: "Lambda Cockpit: Einstellungen"
---

# Lambda Cockpit: Einstellungen

*Zuletzt geändert am 27.11.2026*

Der Tab **Einstellungen** im [Lambda Cockpit](lambda-cockpit.md) (Schaltfläche *Einstellungen* im Bereich *Aktionen*) enthält Einstellungen, die das Cockpit selbst betreffen. Sie werden in Home Assistant gespeichert und bleiben beim Neustart und bei einer Aktualisierung des Dashboards erhalten. Die Erklärungen einzelner Kacheln stehen auf [Lambda Cockpit: die Kacheln](lambda-cockpit-kacheln.md).

Das Symbol **?** oben im Fenster führt direkt zu dieser Seite.

## Puffer-Sollwert

Der Puffer-Sollwert ist die Temperatur, auf die die Lambda den Pufferspeicher heizt. Das Cockpit bezieht ihn in dieser Reihenfolge:

1. **Ausgewählter Sensor:** Wenn Sie unter *Puffer-Sollwert* einen Temperatursensor auswählen, zeigt das Cockpit dessen Wert.
2. **Wert der Lambda:** Ohne Auswahl nimmt das Cockpit den Sollwert, den die Lambda für den Puffer meldet (Register 3004, Sensor `buff1_buffer_temperature_high_setpoint`).
3. **Ausweichrechnung:** Nur wenn Sie sie einschalten und beides fehlt (siehe unten).

Im Auswahlfeld stehen alle Temperatursensoren, die Home Assistant kennt, unabhängig von der Integration, aus der sie stammen. Das ist nützlich, wenn der Puffer über einen eigenen Fühler oder ein Thermometer gemessen wird.

## Ausweichrechnung

Die Ausweichrechnung füllt den Puffer-Sollwert aus, wenn die Lambda keinen Wert liefert und kein Sensor gewählt ist. Sie ist **standardmäßig aus**: Ein falscher Wert ist schlechter als gar keiner.

Ist sie eingeschaltet, rechnet das Cockpit:

> **Puffer-Sollwert = höchster Heizkreis-Sollwert + Puffer-Offset + PV-Zuschlag**

- **Höchster Heizkreis-Sollwert:** Bei mehreren Heizkreisen zählt der höchste Vorlauf-Sollwert aller Heizkreise. Der Puffer folgt dem wärmsten Kreis.
- **Puffer-Offset:** die Einstellung *Solltemperaturoffset Heizbetrieb* am Lambda-Display (als Kopie in der Entität `buffer_setpoint_offset`, Standard 1,0 K).
- **PV-Zuschlag:** nur wenn PV-Überschuss gerade aktiv ist.

Das Ergebnis wird nur angezeigt, wenn es zwischen 0 und 90 °C liegt. Sonst bleibt die Anzeige leer („–“), und die Schaltpunkte des Puffers gelten als nicht berechenbar.

!!! note "Die Ausweichrechnung ist eine Näherung"
    Sie nimmt an, dass der Puffer genau so viel über dem Heizkreis-Sollwert liegt, wie der Offset angibt. Ob das bei Ihrer Anlage stimmt, prüfen Sie am Display. Stimmt der Wert der Lambda, brauchen Sie die Ausweichrechnung nicht.

## Heizkörper oder Fußbodenheizung

Die Kachel des Heizkreises zeichnet je nach Einstellung Heizkörper oder Fußbodenheizung. Die Auswahl gilt je Heizkreis. Bei einem Heizkreis steht sie auf der Hauptseite, bei weiteren Heizkreisen in deren Reiter.

Die Einstellung hat Vorrang vor `heating_type` in der YAML-Konfiguration einer Karte.

## Wo die Werte gespeichert werden

Die Einstellungen liegen in Home Assistant, nicht im Browser und nicht im Dashboard. Sie überstehen daher:

- das Neuschreiben des Dashboards, etwa nach einer Änderung des Layouts,
- Neustarts von Home Assistant,
- Aktualisierungen der Integration.

Sie gelten für alle Browser und Geräte, die das Cockpit anzeigen.
