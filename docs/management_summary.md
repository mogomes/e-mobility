# Management Summary

Für die Praxisarbeit wurde eine internetfähige Webapplikation für den Verleih und die Verwaltung von E-Scootern umgesetzt. Die Lösung basiert auf Flask als Web-Framework, PostgreSQL als relationalem Datenbanksystem und Gunicorn als produktionsfähigem WSGI-Server. Optional kann Nginx als Reverse Proxy vorgeschaltet werden.

Der geschäftliche Mehrwert der Lösung liegt in der sauberen Trennung von Benutzerverwaltung, Scooter-Verwaltung, Ausleihprozess und API-Zugriff. Dadurch kann die Anwendung sowohl interaktiv im Browser als auch automatisiert über API-Clients wie curl oder Postman genutzt werden.

Das grösste Risiko liegt im produktiven Betrieb: Ohne konsequente Absicherung von Secrets, Firewall, HTTPS und Backups kann ein öffentlich erreichbarer Server missbräuchlich genutzt werden. Für den produktiven Einsatz sollten daher ein Reverse Proxy, TLS-Zertifikate, ein restriktives Firewall-Setup und regelmässige Datenbank-Backups eingesetzt werden.

Die Lösung ist wartbar, weil sie modular mit Flask-Blueprints aufgebaut wurde. Sie ist skalierbar, weil App- und Datenbankschicht logisch getrennt sind. Die Verfügbarkeit kann durch systemd, Docker oder einen Reverse Proxy verbessert werden.
