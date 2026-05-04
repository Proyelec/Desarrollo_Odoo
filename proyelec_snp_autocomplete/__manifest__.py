{
    "name": "Proyelec SNP Autocomplete",
    "version": "17.0.1.0.0",
    "category": "Inventory",
    "summary": "Autocompletado y validación de correlativos SNP en productos.",
    "description": """
        Cuando el usuario escribe un prefijo tipo 'TORSNP' en el campo
        código interno (default_code), el sistema detecta automáticamente
        el último correlativo usado y sugiere el siguiente disponible.

        Además valida que el formato del código SNP sea correcto y advierte
        si el correlativo ingresado manualmente está fuera de secuencia.
    """,
    "author": "Proyelec / Contables Boyer",
    "license": "LGPL-3",
    "depends": [
        "product",
        "product_default_code_unique_required",
    ],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}