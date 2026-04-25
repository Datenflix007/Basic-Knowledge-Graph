from __future__ import annotations

from .graph import KnowledgeGraph


def add_rescue_service_tbox(kg: KnowledgeGraph) -> None:
    """Add a small DIN EN 1789 oriented TBox for rescue-service vehicles.

    The extracted excerpts remain the ABox layer. These classes provide a
    transparent schema layer for class-based exploration and later RAG chunking.
    """
    vehicle = kg.add_class(
        "Rettungsdienstfahrzeug",
        aliases=["bodengebundenes Rettungsdienstfahrzeug", "Rettungsmittel"],
        description="Oberklasse fuer normativ beschriebene Fahrzeuge des bodengebundenen Rettungsdienstes.",
    )
    ktw = kg.add_class(
        "Krankentransportwagen",
        aliases=["KTW", "Typ A"],
        description="DIN-EN-1789-Fahrzeuggruppe Typ A fuer Krankentransport.",
    )
    ktw_a1 = kg.add_class(
        "Krankentransportwagen Typ A1",
        aliases=["KTW Typ A1", "Typ A1"],
        description="Unterklasse des Krankentransportwagens nach DIN EN 1789.",
    )
    ktw_a2 = kg.add_class(
        "Krankentransportwagen Typ A2",
        aliases=["KTW Typ A2", "Typ A2"],
        description="Unterklasse des Krankentransportwagens nach DIN EN 1789.",
    )
    emergency_ambulance = kg.add_class(
        "Notfallkrankenwagen",
        aliases=["KTW Typ B", "Typ B"],
        description="DIN-EN-1789-Fahrzeuggruppe Typ B.",
    )
    ambulance = kg.add_class(
        "Rettungswagen (Typ C)",
        aliases=["Rettungswagen", "RTW", "Typ C", "KTW Typ C"],
        description="DIN-EN-1789-Fahrzeuggruppe Typ C fuer erweiterte Behandlung und Ueberwachung.",
    )
    standard = kg.add_class(
        "DIN EN 1789",
        aliases=["DIN", "DIN EN 1789:2020-12"],
        description="Normativer Bezug fuer bodengebundene Rettungsdienstfahrzeuge und deren Ausstattung.",
    )

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
