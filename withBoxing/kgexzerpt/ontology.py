from __future__ import annotations

from .graph import KnowledgeGraph


def add_domain_tbox(kg: KnowledgeGraph) -> None:
    """Add a domain TBox for the extracted rescue-service security graph.

    The extracted excerpts remain the ABox. The TBox gives the whole graph a
    transparent class layer: entity-type classes, rescue-service classes,
    IT-security classes, standards, components, interfaces and vulnerabilities.
    """
    thing = kg.add_class(
        "Wissensgraph-Gegenstand",
        aliases=["Gegenstand", "Entitaet", "Entity"],
        description="Oberklasse fuer alle fachlich klassifizierbaren ABox-Knoten.",
    )
    concept = kg.add_class(
        "Konzept",
        aliases=["Concept", "Begriff", "Sachkonzept"],
        entity_kinds=["Concept", "MISC"],
        description="Abstrakte oder fachliche Begriffe aus den Exzerpten.",
    )
    actor = kg.add_class(
        "Akteur",
        aliases=["Person", "Organisation", "Institution"],
        keywords=["akteur", "anwender", "anwendende", "hersteller", "organisation", "dachorganisation", "forschung"],
        description="Personen, Organisationen und institutionelle Akteure.",
    )
    person = kg.add_class("Person", aliases=["PER"], entity_kinds=["PER"], keywords=["person", "autor"])
    organisation = kg.add_class(
        "Organisation",
        aliases=["ORG", "BSI", "FZI", "Bundesamt fuer Sicherheit in der Informationstechnik"],
        entity_kinds=["ORG"],
        keywords=["bsi", "fzi", "organisation", "dachorganisation", "leitstelle", "klinik", "hersteller"],
    )
    place = kg.add_class("Ort", aliases=["LOC", "Standort"], entity_kinds=["LOC"], keywords=["ort", "deutschland", "nahbereich"])

    rescue = kg.add_class(
        "Rettungsdienst",
        aliases=["bodengebundener Rettungsdienst", "Rettungsdienste", "Rettungswesen"],
        keywords=["rettungsdienst", "rettungswagen", "krankentransport", "rtw", "ktw", "daseinsvorsorge", "gefahrenabwehr"],
        description="Fachlicher Kontext der untersuchten Systeme und Fahrzeuge.",
    )
    public_service = kg.add_class(
        "Daseinsvorsorge und Gefahrenabwehr",
        aliases=["Daseinsvorsorge", "Gefahrenabwehr"],
        keywords=["daseinsvorsorge", "gefahrenabwehr", "landesgesetz", "verordnung"],
    )
    vehicle = kg.add_class(
        "Rettungsdienstfahrzeug",
        aliases=["bodengebundenes Rettungsdienstfahrzeug", "Rettungsmittel"],
        keywords=["rettungsdienstfahrzeug", "rettungsmittel", "fahrzeug", "rtw", "ktw", "krankentransportwagen"],
        description="Oberklasse fuer normativ beschriebene Fahrzeuge des bodengebundenen Rettungsdienstes.",
    )
    ktw = kg.add_class(
        "Krankentransportwagen",
        aliases=["KTW", "Typ A"],
        keywords=["krankentransportwagen", "ktw", "typ a"],
        description="DIN-EN-1789-Fahrzeuggruppe Typ A fuer Krankentransport.",
    )
    ktw_a1 = kg.add_class(
        "Krankentransportwagen Typ A1",
        aliases=["KTW Typ A1", "Typ A1"],
        keywords=["typ a1", "ktw typ a1"],
        description="Unterklasse des Krankentransportwagens nach DIN EN 1789.",
    )
    ktw_a2 = kg.add_class(
        "Krankentransportwagen Typ A2",
        aliases=["KTW Typ A2", "Typ A2"],
        keywords=["typ a2", "ktw typ a2"],
        description="Unterklasse des Krankentransportwagens nach DIN EN 1789.",
    )
    emergency_ambulance = kg.add_class(
        "Notfallkrankenwagen",
        aliases=["KTW Typ B", "Typ B"],
        keywords=["notfallkrankenwagen", "typ b", "ktw typ b"],
        description="DIN-EN-1789-Fahrzeuggruppe Typ B.",
    )
    ambulance = kg.add_class(
        "Rettungswagen (Typ C)",
        aliases=["Rettungswagen", "RTW", "Typ C", "KTW Typ C"],
        keywords=["rettungswagen", "rtw", "typ c", "ktw typ c"],
        description="DIN-EN-1789-Fahrzeuggruppe Typ C fuer erweiterte Behandlung und Ueberwachung.",
    )
    standard = kg.add_class(
        "DIN EN 1789",
        aliases=["DIN", "DIN EN 1789:2020-12"],
        keywords=["din en 1789", "din", "mindeststandard", "norm"],
        description="Normativer Bezug fuer bodengebundene Rettungsdienstfahrzeuge und deren Ausstattung.",
    )
    medical_product = kg.add_class(
        "Medizinprodukt",
        aliases=["medizinisches Geraet", "medizinisches Produkt", "Geraet"],
        keywords=["medizinprodukt", "geraet", "defibrillator", "beatmungsgeraet", "thoraxkompressionsgeraet", "patientenmonitor", "spritzenpumpe", "infusionspumpe"],
        description="Untersuchte medizinische Produkte und Geraeteklassen.",
    )
    networked_system = kg.add_class(
        "Vernetztes System",
        aliases=["vernetztes System", "IT-System", "Software-System", "Produkt"],
        keywords=["system", "produkt", "tablet", "server", "software", "plattform", "webanwendung", "cloud", "android", "steuergeraet"],
        description="Digitale oder vernetzte Produkt- und Systembestandteile.",
    )
    interface = kg.add_class(
        "Schnittstelle",
        aliases=["Interface", "Benutzerschnittstelle"],
        keywords=["schnittstelle", "usb", "nfc", "bluetooth", "weboberflaeche", "api", "kommunikation", "benutzerschnittstelle"],
    )
    wireless = kg.add_class(
        "Drahtlose Kommunikation",
        aliases=["Funkkommunikation", "Bluetooth", "BLE", "NFC", "WLAN"],
        keywords=["bluetooth", "ble", "nfc", "wlan", "drahtlos", "funk", "wireless"],
    )
    security = kg.add_class(
        "IT-Sicherheit",
        aliases=["Cybersecurity", "Informationssicherheit", "Sicherheitsuntersuchung"],
        keywords=["it-sicherheit", "sicherheit", "sicherheitsuntersuchung", "bedrohung", "angriff", "schutz", "risiko"],
        description="Sicherheitsbezogener Oberbegriff fuer Untersuchung, Befunde und Massnahmen.",
    )
    vulnerability = kg.add_class(
        "Schwachstelle",
        aliases=["Vulnerability", "Sicherheitsluecke", "Befund"],
        keywords=["schwachstelle", "schwachstellen", "luecke", "umgehung", "manipulation", "dos", "brute-force", "hartkodiert", "unzureichend", "ungesichert"],
    )
    attack = kg.add_class(
        "Angriff und Angriffsmodell",
        aliases=["Angriff", "Angreifer", "Angriffsvektor", "Bedrohungsanalyse"],
        keywords=["angriff", "angreifer", "angriffsvektor", "bedrohung", "bedrohungsanalyse", "nahbereich", "physisch", "jamming"],
    )
    cryptography = kg.add_class(
        "Kryptographie und Verschluesselung",
        aliases=["Verschluesselung", "TLS", "BitLocker", "TPM", "VPN"],
        keywords=["verschluesselung", "kryptographie", "tls", "bitlocker", "tpm", "vpn", "schluessel", "passwort", "zertifikat"],
    )
    data = kg.add_class(
        "Daten und Datenschutz",
        aliases=["Daten", "Patientendaten", "Gesundheitsdaten"],
        keywords=["daten", "patientendaten", "gesundheitsdaten", "datenschutz", "datenextraktion", "einsatzdaten", "datensparsam"],
    )
    update = kg.add_class(
        "Firmware und Update",
        aliases=["Firmware", "Update", "Bootloader", "ROM"],
        keywords=["firmware", "update", "updatemechanismus", "bootloader", "rom", "konfigurationsdatei", "wartung", "servicetechnik"],
    )
    standard_class = kg.add_class(
        "Norm und Standard",
        aliases=["Norm", "Standard", "Mindeststandard"],
        keywords=["norm", "standard", "din", "iso", "mindeststandard", "anforderung"],
    )

    for child in [concept, actor, rescue, medical_product, networked_system, security, standard_class]:
        kg.add_class_relation(child, thing, "SUBCLASS_OF")
    for child in [person, organisation]:
        kg.add_class_relation(child, actor, "SUBCLASS_OF")
    kg.add_class_relation(place, thing, "SUBCLASS_OF")
    kg.add_class_relation(public_service, rescue, "RELATED_TO")
    kg.add_class_relation(vehicle, rescue, "SUBCLASS_OF")
    kg.add_class_relation(medical_product, rescue, "USED_IN")
    kg.add_class_relation(networked_system, rescue, "USED_IN")
    kg.add_class_relation(interface, networked_system, "PART_OF")
    kg.add_class_relation(wireless, interface, "SUBCLASS_OF")
    kg.add_class_relation(vulnerability, security, "SUBCLASS_OF")
    kg.add_class_relation(attack, security, "SUBCLASS_OF")
    kg.add_class_relation(cryptography, security, "SECURITY_MEASURE")
    kg.add_class_relation(data, security, "PROTECTS_OR_ENDANGERS")
    kg.add_class_relation(update, networked_system, "PART_OF")
    kg.add_class_relation(standard, standard_class, "SUBCLASS_OF")

    for child in [ktw, emergency_ambulance, ambulance]:
        kg.add_class_relation(child, vehicle, "SUBCLASS_OF")
    for child in [ktw_a1, ktw_a2]:
        kg.add_class_relation(child, ktw, "SUBCLASS_OF")

    kg.add_class_relation(ktw, standard, "DEFINED_BY")
    kg.add_class_relation(emergency_ambulance, standard, "DEFINED_BY")
    kg.add_class_relation(ambulance, standard, "DEFINED_BY")
    kg.add_class_relation(ambulance, ktw, "RELATED_BUT_DISTINCT_FROM", note="Typ C wird umgangssprachlich teils mit KTW-Schemata vermischt, ist normativ aber Rettungswagen.")
    kg.add_synonym(ambulance, "Rettungswagen")
    kg.add_synonym(ambulance, "RTW")
    kg.add_synonym(ambulance, "KTW Typ C")
    kg.add_synonym(organisation, "BSI")
    kg.add_synonym(organisation, "FZI")
    kg.add_synonym(cryptography, "TLS 1.3")
    kg.add_synonym(cryptography, "BitLocker")
    kg.add_synonym(wireless, "Bluetooth")
    kg.add_synonym(wireless, "NFC")
    kg.add_synonym(data, "Patientendaten")


def add_rescue_service_tbox(kg: KnowledgeGraph) -> None:
    """Backward-compatible alias for older callers."""
    add_domain_tbox(kg)
