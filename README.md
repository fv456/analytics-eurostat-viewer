# Eurostat Digital economy and society Dashboard

Cruscotto di analytics per la visualizzazione di una selezione di informazioni presenti nei dataset Eurostat scaricabili a [questo link](https://ec.europa.eu/eurostat/web/digital-economy-and-society/data/comprehensive-database).

Pagine presenti nella web app:

- **bde15cua treemaps:** Confronto nell'uso di internet da parte dei cittadini e delle famiglie in Italia e nei Paesi UE.

- **digital skills boxplots:** Confronto delle competenze digitali tra l'Italia e gli altri Paesi UE, con l'uso di grafici boxplot.

- **digital skills treemaps:** Confronto delle competenze digitali tra l'Italia e gli altri Paesi UE, con l'uso di grafici treemap.

- **ict in enterprises:** Confronto nell'uso dell'ICT nelle imprese tra l'Italia e gli altri Paesi UE.

- **nuts2 bars:** Confronto tra regioni italiane per tutti i dati presenti all'interno del database Eurostat dedicato alle famiglie e agli individui che abbiano granularità regionale (NUTS2)


Tutte le web app, per ragioni di performance, fanno uso di varie pre-elaborazioni del suddetto database all'interno della cartella **data/**.

Lo script di preprocessing non è al momento incluso nel repository.


## Da completare:
- Aggiunta degli script di preprocessing che permettano di ottenere i dataset di cui fa uso la web app




## Licenza:

    Copyright (c) the respective contributors, as shown by the AUTHORS file.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.