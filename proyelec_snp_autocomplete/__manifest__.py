{
    "name": "Proyelec SNP Autocomplete",
    "version": "17.0.1.0.0",
    "category": "Inventory",
    "summary": "Autocompletado y validacion de correlativos SNP en productos.",
    "description": """
        Cuando el usuario escribe un prefijo tipo TORSNP en el campo
        codigo interno (default_code), el sistema detecta automaticamente
        el ultimo correlativo usado y sugiere el siguiente disponible.

        Ademas valida que el formato del codigo SNP sea correcto y advierte
        si el correlativo ingresado manualmente esta fuera de secuencia.
    """,
    "author": "Proyelec / Contables Boyer",
    "license": "LGPL-3",
    "depends": [
        "product",
        "product_default_code_unique_required",
    ],
    "data": [
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}