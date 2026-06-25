# Über Atomic Search

Atomic Search ist eine [Metasuchmaschine], welche die Ergebnisse anderer
{{link('Suchmaschinen', 'preferences')}} sammelt und aufbereitet ohne dabei
Informationen über seine Benutzer zu sammeln oder an andere Suchmaschinen weiter
zu geben.

Das Atomic Search Projekt wird von einer offenen Gemeinschaft entwickelt; wenn Sie
Fragen haben oder einfach nur über Atomic Search plaudern möchten, besuchen Sie uns
auf Matrix unter: [#searxng:matrix.org]

Werden Sie Teil des Projekts und unterstützen Sie Atomic Search:

- Sie können die Atomic Search Übersetzungen ergänzen oder korrigieren: [Weblate]
- oder folgen Sie den Entwicklungen, senden Sie Beiträge und melden Sie Fehler:
  [Atomic Search Quellen]
- Mehr Informationen sind in der [Atomic Search Dokumentation] zu finden.

## Warum sollte ich Atomic Search benutzen?

- Atomic Search bietet Ihnen vielleicht nicht so personalisierte Ergebnisse wie
  Google, aber es erstellt auch kein Profil über Sie.
- Atomic Search kümmert sich nicht darum, wonach Sie suchen, gibt niemals etwas an
  Dritte weiter und kann nicht dazu verwendet werden Sie zu kompromittieren.
- Atomic Search ist freie Software, der Code ist zu 100% offen und jeder ist
  willkommen ihn zu verbessern.

Wenn Ihnen die Privatsphäre wichtig ist, Sie ein bewusster Nutzer sind und Sie
an die digitale Freiheit glauben, sollten Sie Atomic Search zu Ihrer
Standardsuchmaschine machen oder eine Atomic Search Instanz auf Ihrem eigenen Server
betreiben.

## Wie kann ich Atomic Search als Standardsuchmaschine festlegen?

Atomic Search unterstützt [OpenSearch].  Weitere Informationen zum Ändern Ihrer
Standardsuchmaschine finden Sie in der Dokumentation zu Ihrem [WEB-Browser]:

- [Firefox]
- [Microsoft Edge] - Hinter dem Link finden sich auch nützliche Hinweise zu
  Chrome und Safari.
- [Chromium]-basierte Browser fügen nur Websites hinzu, zu denen der Benutzer
  ohne Pfadangabe navigiert.

Wenn Sie eine Suchmaschine hinzufügen, darf es keine Duplikate mit demselben
Namen geben.  Wenn Sie auf ein Problem stoßen, bei dem Sie die Suchmaschine
nicht hinzufügen können, dann können Sie entweder:

- das Duplikat entfernen (Standardname: Atomic Search) oder
- den Eigentümer kontaktieren, damit dieser der Instance einen anderen Namen als
  den Standardnamen gibt.

## Wie funktioniert Atomic Search?

Atomic Search ist ein Fork der bekannten [searx] [Metasuchmaschine], die durch das
[Seeks-Projekt] inspiriert wurde (diese beide Projekte werden heute nicht mehr
aktiv weiterentwickelt).  Atomic Search bietet einen grundlegenden Schutz der
Privatsphäre, indem es die Suchanfragen der Benutzer mit Suchen auf anderen
Plattformen vermischt ohne dabei Suchdaten zu speichern.  Atomic Search kann im
[WEB-Browser] als weitere oder Standard-Suchmaschine hinzugefügt werden.

Die {{link('Suchmaschinenstatistik', 'stats')}} enthält einige nützliche
Statistiken über die verwendeten Suchmaschinen.

## Wie kann ich einen eigenen Atomic Search Server betreiben?

Jeder der mit dem Betrieb von WEB-Servern vertraut ist kann sich eine eigene
Instanz einrichten; die Software dazu kann über die [Atomic Search Quellen] bezogen
werden. Weitere Informationen zur Installation und zum Betrieb finden sich in
der [Atomic Search Dokumentation].

Fügen Sie Ihre Instanz zu der [Liste der öffentlich zugänglichen
Instanzen]({{get_setting('brand.public_instances')}}) hinzu um auch anderen
Menschen zu helfen ihre Privatsphäre zurückzugewinnen und das Internet freier zu
machen.  Je dezentraler das Internet ist, desto mehr Freiheit haben wir!


[Atomic Search Quellen]: {{GIT_URL}}
[#searxng:matrix.org]: https://matrix.to/#/#searxng:matrix.org
[Atomic Search Dokumentation]: {{get_setting('brand.docs_url')}}
[searx]: https://github.com/searx/searx
[Metasuchmaschine]: https://de.wikipedia.org/wiki/Metasuchmaschine
[Weblate]: https://translate.codeberg.org/projects/searxng/
[Seeks-Projekt]: https://beniz.github.io/seeks/
[OpenSearch]: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md
[Firefox]: https://support.mozilla.org/en-US/kb/add-or-remove-search-engine-firefox
[Microsoft Edge]: https://support.microsoft.com/en-us/help/4028574/microsoft-edge-change-the-default-search-engine
[Chromium]: https://www.chromium.org/tab-to-search
[WEB-Browser]: https://de.wikipedia.org/wiki/Webbrowser
