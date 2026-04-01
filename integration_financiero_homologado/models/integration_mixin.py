# /integration_financiero_homologado/models/integration_mixin.py
import xmlrpc.client
import logging
import time
from odoo import models, fields, _, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IntegrationMixin(models.AbstractModel):
    _name = "integration.mixin"
    _description = "Mixin para integración con DB Homologada"

    homologado_id = fields.Integer(
        string="ID Destino", readonly=True, copy=False, index=True
    )

    def _get_homologado_credentials(self):
        """Obtiene las credenciales de los parámetros del sistema de forma segura."""
        config = self.env["ir.config_parameter"].sudo()
        url = config.get_param("homologado.db.url")
        db = config.get_param("homologado.db.name")
        username = config.get_param("homologado.db.user")
        password = config.get_param("homologado.db.password")

        if not all([url, db, username, password]):
            raise UserError(
                _(
                    "La configuración de la API para la base de datos homologada no está completa. Contacte al administrador."
                )
            )

        return url, db, username, password

    def _get_remote_models_proxy(self):
        """
        ✅ FUNCIÓN ACTUALIZADA: No se necesita un transporte personalizado.
        La clave es 'allow_none=True' en el ServerProxy.
        """
        url, db, username, password = self._get_homologado_credentials()
        try:
            # Ya no necesitamos la instancia de AllowNoneTransport

            common_url = f"{url}/xmlrpc/2/common"
            object_url = f"{url}/xmlrpc/2/object"

            # Pasamos 'allow_none=True' directamente al constructor
            common = xmlrpc.client.ServerProxy(
                common_url, verbose=False, allow_none=True  # <-- La clave
            )
            uid = common.authenticate(db, username, password, {})
            if not uid:
                raise UserError(
                    _(
                        "Autenticación fallida con la base de datos homologada. Verifique las credenciales."
                    )
                )

            models_proxy = xmlrpc.client.ServerProxy(
                object_url, verbose=False, allow_none=True  # <-- La clave
            )
            return models_proxy, db, uid, password
        except Exception as e:
            _logger.error("Error de conexión con Odoo Homologado: %s", str(e))
            raise UserError(
                _(f"Ocurrió un error al contactar la base de datos homologada:\n{e}")
            )

    def _find_remote_id(
        self, models_proxy, db, uid, password, model_name, search_fields, value
    ):
        """
        Encuentra el ID de un registro en la DB remota usando un valor en una lista de campos posibles.
        """
        if not value:
            raise UserError(
                _(
                    f"El valor de búsqueda para el modelo '{model_name}' está vacío. No se puede continuar."
                )
            )

        if isinstance(search_fields, str):
            search_fields = [search_fields]

        # ✅ CORRECCIÓN DEFINITIVA: Construir el dominio de forma plana (notación polaca).
        # Esto genera un dominio como: ['|', '|', ('vat', '=', V), ('identification_id', '=', V), ('rif', '=', V)]
        # Es una lista simple, sin anidaciones, y es la forma más robusta.
        domain = []
        # Añadimos un operador '|' por cada 'OR' que necesitamos. Para 3 campos, se necesitan 2 '|'.
        for i in range(len(search_fields) - 1):
            domain.append("|")
        # Ahora añadimos todas las condiciones de búsqueda (hojas).
        for field in search_fields:
            domain.append((field, "=", value))

        try:
            _logger.info(
                "Buscando en Homologado - Modelo: %s, Dominio: %s", model_name, domain
            )
            remote_ids = models_proxy.execute_kw(
                db, uid, password, model_name, "search", [domain], {"limit": 1}
            )

            if not remote_ids:
                raise UserError(
                    _(
                        f"No se encontró el registro en la DB Homologada:\n\n"
                        f"**Modelo:** `{model_name}`\n"
                        f"**Campos buscados:** `{', '.join(search_fields)}`\n"
                        f"**Valor buscado:** `{value}`"
                    )
                )
            return remote_ids[0]
        except Exception as e:
            _logger.error(
                "Error buscando ID remoto para %s con %s=%s: %s",
                model_name,
                search_fields,
                value,
                str(e),
            )
            # Analizamos si el error remoto es por un campo que no existe
            if "Invalid field" in str(e):
                raise UserError(
                    _(
                        "Error de configuración: Uno de los campos de búsqueda (%s) no existe en el modelo '%s' de la base de datos homologada."
                    )
                    % (", ".join(search_fields), model_name)
                )

            raise UserError(
                _(
                    "Error de comunicación buscando un registro relacionado en la base de datos de destino. Revise los logs. "
                    "Probablemente el contacto no existe en la Base de Datos destino."
                )
            )

    def _find_remote_product_id(self, models_proxy, db, uid, password, product):
        """
        Busca un product.product remoto:
        - Primero por referencia interna exacta (default_code).
        - Si no hay default_code, intenta por nombre exacto.
        Mensajes claros si falta referencia interna o no hay coincidencias.
        """
        if not product:
            raise UserError(
                _(
                    "No se proporcionó un producto para buscar en la Base de datos destino."
                )
            )

        name = product.name or product.display_name or ""
        code = product.default_code or False

        if not name:
            raise UserError(_("El producto seleccionado no tiene nombre definido."))

        # Dominio: por código o por nombre exacto
        if code:
            domain = ["|", ("default_code", "=", code), ("name", "=", name)]
        else:
            _logger.warning(
                "Producto sin referencia interna (default_code). Se intentará buscar por nombre exacto: %s",
                name,
            )
            domain = [("name", "=", name)]

        try:
            _logger.info(
                "Buscando en base de datos - Modelo: %s, Dominio: %s",
                "product.product",
                domain,
            )
            ids = models_proxy.execute_kw(
                db, uid, password, "product.product", "search", [domain], {"limit": 1}
            )
            if not ids:
                if code:
                    raise UserError(
                        _(
                            "No se encontró el producto en la Base de datos destino por referencia interna '%s' ni por nombre exacto '%s'."
                        )
                        % (code, name)
                    )
                else:
                    raise UserError(
                        _(
                            "El producto '%s' no tiene Referencia Interna definida y tampoco se encontró un producto con nombre exacto en la Base de datos destino."
                        )
                        % (name,)
                    )
            return ids[0]
        except Exception as e:
            _logger.error(
                "Error buscando producto remoto por código/nombre: %s", str(e)
            )
            raise UserError(
                _(
                    "Error consultando la Base de datos destino para el producto '%s'. Detalle: %s"
                )
                % (name, str(e))
            )

    def _get_fixed_remote_user_id(self, models_proxy, db, uid, password):
        """
        Obtiene el usuario remoto fijo por login.
        Prioriza 'homologado.db.fixed_user_login' y, si no existe,
        usa el usuario API configurado en 'homologado.db.user'.
        """
        config = self.env["ir.config_parameter"].sudo()
        fixed_login = (config.get_param("homologado.db.fixed_user_login") or "").strip()

        if not fixed_login:
            fixed_login = (config.get_param("homologado.db.user") or "").strip()

        if not fixed_login:
            raise UserError(
                _(
                    "No hay un login de usuario fijo configurado para la integración. "
                    "Defina 'homologado.db.fixed_user_login' o revise 'homologado.db.user'."
                )
            )

        try:
            return self._find_remote_id(
                models_proxy,
                db,
                uid,
                password,
                "res.users",
                "login",
                fixed_login,
            )
        except UserError as e:
            raise UserError(
                _(
                    "No se encontró el usuario fijo '%s' en la base de datos destino. "
                    "Cree el usuario o ajuste la configuración.\nDetalle: %s"
                )
                % (fixed_login, str(e))
            )

    def _action_send_to_homologado_generic(
        self, remote_model, vals, confirm_method=None, invoice_method=None
    ):
        """
        Método genérico final para crear, confirmar y facturar el documento remoto.

        ✅ ACTUALIZADO:
        1. Se elimina el try/except para 'xmlrpc.client.Fault' (se asume allow_none=True).
        2. Se añade un bucle de reintento para la búsqueda de facturas y evitar 'race conditions'.
        """
        self.ensure_one()
        if self.homologado_id:
            raise UserError(
                _("Este documento ya fue enviado y registrado con el ID: %s")
                % self.homologado_id
            )

        models_proxy, db, uid, password = self._get_remote_models_proxy()

        # --- PASO 1: Crear el documento ---
        _logger.info(
            "Creando documento remoto en '%s' con valores: %s", remote_model, vals
        )
        new_remote_id = models_proxy.execute_kw(
            db, uid, password, remote_model, "create", [vals]
        )

        # Obtener el nombre real del documento remoto
        remote_data = models_proxy.execute_kw(
            db, uid, password, remote_model, "read", [[new_remote_id], ["name"]]
        )
        remote_name = remote_data[0]["name"] if remote_data else self.name
        _logger.info("Nombre del documento remoto creado: %s", remote_name)

        self.write({"homologado_id": new_remote_id})
        self.message_post(
            body=_(
                f"✅ Documento enviado con éxito. ID Destino: {new_remote_id} ({remote_name})"
            )
        )

        # --- PASO 2: Confirmar el documento ---
        if confirm_method:
            try:
                _logger.info(
                    "Confirmando documento remoto ID %s con método '%s'",
                    new_remote_id,
                    confirm_method,
                )
                models_proxy.execute_kw(
                    db, uid, password, remote_model, confirm_method, [[new_remote_id]]
                )
                self.message_post(
                    body=_("✅ Documento confirmado en la base de datos destino.")
                )
            except Exception as e:
                msg = _(
                    "Falló la confirmación automática del documento remoto: %s"
                ) % str(e)
                self.message_post(body=msg)
                raise UserError(msg)

        # --- PASO 3: Crear la factura borrador ---
        if invoice_method:
            try:
                _logger.info(
                    "Iniciando creación de factura remota para ID %s", new_remote_id
                )

                # Lógica para Ventas (sale.order)
                if remote_model == "sale.order":
                    context = {
                        "active_model": "sale.order",
                        "active_ids": [new_remote_id],
                    }
                    wizard_vals = {"advance_payment_method": "delivered"}
                    wizard_id = models_proxy.execute_kw(
                        db,
                        uid,
                        password,
                        "sale.advance.payment.inv",
                        "create",
                        [wizard_vals],
                        {"context": context},
                    )

                    # ✅ CORRECCIÓN: Llamada directa. Ya no se espera un error 'Fault'.
                    # Esta llamada devolverá 'None' (o una acción) y no fallará gracias a 'allow_none=True'.
                    # ✅ CORRECCIÓN: Llamada protegida contra 'cannot marshal None'
                    try:
                        models_proxy.execute_kw(
                            db,
                            uid,
                            password,
                            "sale.advance.payment.inv",
                            "create_invoices",
                            [wizard_id],
                            {"context": context},
                        )
                    except xmlrpc.client.Fault as e:
                        if "cannot marshal None" in str(e):
                            _logger.warning(
                                "Ignorando error de serialización XML-RPC (None return) en create_invoices: %s",
                                e,
                            )
                        else:
                            raise e

                    # ✅ PRO-TIP: Búsqueda robusta con reintentos para evitar 'race conditions'
                    invoice_ids = []
                    search_domain = [
                        [
                            ("invoice_origin", "=", remote_name),
                            ("move_type", "=", "out_invoice"),
                        ]
                    ]
                    max_retries = 5
                    retry_delay_seconds = 5

                    for attempt in range(max_retries):
                        _logger.info(
                            f"Buscando factura remota (Intento {attempt + 1}/{max_retries})..."
                        )
                        invoice_ids = models_proxy.execute_kw(
                            db,
                            uid,
                            password,
                            "account.move",
                            "search",
                            search_domain,
                            {"limit": 1},
                        )
                        if invoice_ids:
                            _logger.info(
                                f"¡Factura remota encontrada! ID: {invoice_ids[0]}"
                            )
                            break  # ¡Encontrada! Salir del bucle.

                        if attempt < max_retries - 1:
                            time.sleep(
                                retry_delay_seconds
                            )  # Esperar antes de reintentar

                    # Comprobación final después de todos los reintentos
                    if not invoice_ids:
                        raise UserError(
                            _(
                                "Se ejecutó la creación de factura, pero no se pudo encontrar en la Base de datos destino para el origen %s después de %s intentos. Verifique manually."
                            )
                            % (self.name, max_retries)
                        )

                    self.write({"homologado_invoice_id": invoice_ids[0]})
                    self.message_post(
                        body=_(
                            "✅ Factura borrador creada en la Base de datos destino. ID Factura: %s"
                        )
                        % invoice_ids[0]
                    )

                # Lógica para Compras (purchase.order)
                elif remote_model == "purchase.order":
                    # PASO 3a: Ejecutar el método de creación de factura (ej. 'action_create_invoice')
                    # PASO 3a: Ejecutar el método de creación de factura (ej. 'action_create_invoice')
                    try:
                        models_proxy.execute_kw(
                            db,
                            uid,
                            password,
                            remote_model,
                            invoice_method,
                            [[new_remote_id]],
                        )
                    except xmlrpc.client.Fault as e:
                        if "cannot marshal None" in str(e):
                            _logger.warning(
                                "Ignorando error de serialización XML-RPC (None return) en %s: %s",
                                invoice_method,
                                e,
                            )
                        else:
                            raise e

                    # PASO 3b: Búsqueda robusta (igual que en ventas, pero con 'in_invoice')
                    created_invoice_ids = []
                    search_domain = [
                        [
                            ("invoice_origin", "=", remote_name),
                            ("move_type", "=", "in_invoice"),
                        ]
                    ]
                    max_retries = 5
                    retry_delay_seconds = 5

                    for attempt in range(max_retries):
                        _logger.info(
                            f"Buscando factura de proveedor remota (Intento {attempt + 1}/{max_retries})..."
                        )
                        created_invoice_ids = models_proxy.execute_kw(
                            db,
                            uid,
                            password,
                            "account.move",
                            "search",
                            search_domain,
                            {"limit": 1},
                        )
                        if created_invoice_ids:
                            _logger.info(
                                f"¡Factura de proveedor remota encontrada! ID: {created_invoice_ids[0]}"
                            )
                            break
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay_seconds)

                    if not created_invoice_ids:
                        raise UserError(
                            _(
                                "Se ejecutó la creación de factura de proveedor, pero no se pudo encontrar en la BD homologada para el origen %s después de %s intentos. Verifique manualmente."
                            )
                            % (self.name, max_retries)
                        )

                    self.write({"homologado_invoice_id": created_invoice_ids[0]})
                    self.message_post(
                        body=_(
                            "✅ Factura de proveedor borrador creada en la Base de datos destino. ID Factura: %s"
                        )
                        % created_invoice_ids[0]
                    )

            except Exception as e:
                msg = _(
                    "Falló la creación automática de la factura borrador remota: %s"
                ) % str(e)
                self.message_post(body=msg)
                raise UserError(msg)

        # Forzar recarga de la vista para re-evaluar attrs/invisible del botón
        return {"type": "ir.actions.client", "tag": "reload"}

    def _remote_fields(self, models_proxy, db, uid, password, model_name):
        """Devuelve set de campos existentes en el modelo remoto."""
        info = models_proxy.execute_kw(
            db, uid, password, model_name, "fields_get", [], {"attributes": ["type"]}
        )
        return set(info.keys())

    def _filter_remote_vals(self, vals, remote_fields):
        """Quita del dict los campos que no existen en remoto o que vienen None."""
        clean = {}
        for k, v in vals.items():
            if k in remote_fields and v is not None:
                clean[k] = v
        return clean

    def _get_or_create_remote_uom(self, models_proxy, db, uid, password, uom):
        """
        Busca o crea una UoM remota (y su categoría) por nombre.
        Si la UoM no es de referencia, asegura que la UoM de referencia de la categoría
        se sincronice primero para evitar errores de restricción en Odoo.
        """
        if not uom:
            return False

        # --- 0. Pre-requisito: Si no es referencia, sincronizar la referencia primero ---
        # Esto es vital porque Odoo exige que una categoría tenga una unidad de referencia
        # antes de crear otras unidades (bigger/smaller).
        if uom.uom_type != "reference":
            reference_uom = self.env["uom.uom"].search(
                [
                    ("category_id", "=", uom.category_id.id),
                    ("uom_type", "=", "reference"),
                ],
                limit=1,
            )

            if reference_uom and reference_uom.id != uom.id:
                try:
                    _logger.info(
                        "Sincronizando UoM de referencia '%s' antes de '%s'",
                        reference_uom.name,
                        uom.name,
                    )
                    self._get_or_create_remote_uom(
                        models_proxy, db, uid, password, reference_uom
                    )
                except Exception as e:
                    _logger.warning(
                        "No se pudo sincronizar la UoM de referencia anterior: %s", e
                    )
                    # No lanzamos error aquí para permitir intentar crear la actual si fuera posible,
                    # aunque probablemente fallará más adelante.

        # 1. Buscar UoM
        domain = [("name", "=", uom.name)]
        ids = models_proxy.execute_kw(
            db, uid, password, "uom.uom", "search", [domain], {"limit": 1}
        )
        if ids:
            return ids[0]

        _logger.warning("UoM '%s' no encontrada en destino. Creando...", uom.name)

        try:
            # 2. Buscar o Crear Categoría de UoM
            cat_remote_id = False
            if uom.category_id:
                cat_domain = [("name", "=", uom.category_id.name)]
                cat_ids = models_proxy.execute_kw(
                    db,
                    uid,
                    password,
                    "uom.category",
                    "search",
                    [cat_domain],
                    {"limit": 1},
                )
                if cat_ids:
                    cat_remote_id = cat_ids[0]
                else:
                    cat_vals = {"name": uom.category_id.name}
                    cat_remote_id = models_proxy.execute_kw(
                        db, uid, password, "uom.category", "create", [cat_vals]
                    )
                    _logger.info(
                        "✅ Categoría UoM creada en destino: %s (ID: %s)",
                        uom.category_id.name,
                        cat_remote_id,
                    )

            # 3. Crear UoM
            vals = {
                "name": uom.name,
                "category_id": cat_remote_id,
                "uom_type": uom.uom_type,
                "factor": uom.factor,
                "rounding": uom.rounding,
                "active": True,
            }
            # Unidades de referencia tienen factor 1.0 (en realidad factor inv) pero Odoo lo maneja.
            # Al crear, si es reference, factor debe ser 1.0.

            new_id = models_proxy.execute_kw(
                db, uid, password, "uom.uom", "create", [vals]
            )
            _logger.info("✅ UoM creada en destino: %s (ID: %s)", uom.name, new_id)
            return new_id
        except Exception as e:
            _logger.error("Error creando UoM remota '%s': %s", uom.name, str(e))
            # Fallback crítica: si no tenemos UoM, fallará la creación del producto.
            raise UserError(
                _(
                    "No se pudo sincronizar la Unidad de Medida '%s' necesaria para el producto.\nError: %s"
                )
                % (uom.name, str(e))
            )

    def _get_or_create_remote_product(self, models_proxy, db, uid, password, product):
        """
        Busca producto remoto por default_code o barcode (o name).
        Si no existe, lo crea con campos permitidos.
        Omite campos que no existan en destino.
        """
        if not product:
            raise UserError(_("No se proporcionó un producto."))

        remote_model = "product.product"
        remote_fields = self._remote_fields(
            models_proxy, db, uid, password, remote_model
        )

        name = product.name or product.display_name
        code = product.default_code or False
        barcode = product.barcode or False

        # --- 1) BUSCAR ---
        domain = []
        if code and barcode:
            domain = ["|", ("default_code", "=", code), ("barcode", "=", barcode)]
        elif code:
            domain = [("default_code", "=", code)]
        elif barcode:
            domain = [("barcode", "=", barcode)]
        else:
            domain = [("name", "=", name)]

        ids = models_proxy.execute_kw(
            db, uid, password, remote_model, "search", [domain], {"limit": 1}
        )
        if ids:
            return ids[0]

        # --- 2) CREAR ---
        # Helpers para M2O/M2M
        def find_remote_id(model, field, value):
            if not value:
                return False
            rid = models_proxy.execute_kw(
                db,
                uid,
                password,
                model,
                "search",
                [[(field, "=", value)]],
                {"limit": 1},
            )
            return rid[0] if rid else False

        def find_remote_ids(model, field, values):
            if not values:
                return []
            rids = models_proxy.execute_kw(
                db, uid, password, model, "search", [[(field, "in", values)]]
            )
            return rids or []

        # categ_id (M2O) por nombre
        categ_remote_id = False
        if product.categ_id:
            categ_remote_id = find_remote_id(
                "product.category", "name", product.categ_id.name
            )
            if not categ_remote_id:
                _logger.warning(
                    "Categoría '%s' no encontrada en destino. Creando...",
                    product.categ_id.name,
                )
                try:
                    # Intentamos crear la categoría simple (sin padre por ahora para evitar recursión compleja)
                    categ_vals = {"name": product.categ_id.name}
                    categ_remote_id = models_proxy.execute_kw(
                        db, uid, password, "product.category", "create", [categ_vals]
                    )
                    _logger.info(
                        "✅ Categoría creada en destino: %s (ID: %s)",
                        product.categ_id.name,
                        categ_remote_id,
                    )
                except Exception as e:
                    _logger.error(
                        "Error creando categoría remota '%s': %s",
                        product.categ_id.name,
                        str(e),
                    )
                    # Fallback (opcional): Buscar una categoría por defecto o dejar que falle si es obligatoria

        # product_tag_ids (M2M) por nombre
        tag_names = (
            product.product_tag_ids.mapped("name") if product.product_tag_ids else []
        )
        tag_remote_ids = find_remote_ids("product.tag", "name", tag_names)

        # UoM (M2O) por nombre (usando helper que crea si no existe)
        uom_remote_id = self._get_or_create_remote_uom(
            models_proxy, db, uid, password, product.uom_id
        )
        uom_po_remote_id = self._get_or_create_remote_uom(
            models_proxy, db, uid, password, product.uom_po_id
        )

        vals = {
            "detailed_type": getattr(product, "detailed_type", None),
            "name": name,
            "barcode": barcode,
            "default_code": code,
            "categ_id": categ_remote_id,
            "product_tag_ids": [(6, 0, tag_remote_ids)] if tag_remote_ids else None,
            "weight": product.weight if product.weight is not False else None,
            "volume": product.volume if product.volume is not False else None,
            "sale_ok": product.sale_ok,
            "purchase_ok": product.purchase_ok,
            "uom_id": uom_remote_id,
            "uom_po_id": uom_po_remote_id,
        }

        vals = self._filter_remote_vals(vals, remote_fields)

        new_id = models_proxy.execute_kw(
            db, uid, password, remote_model, "create", [vals]
        )
        _logger.info("Producto creado en destino: %s (%s)", name, new_id)
        return new_id

    def _get_or_create_remote_partner(self, models_proxy, db, uid, password, partner):
        """
        Busca partner remoto por vat/rif/identification_id.
        Si no existe, lo crea con campos permitidos.
        Omite campos que no existan en destino.
        """
        if not partner:
            raise UserError(_("No se proporcionó un partner."))

        remote_model = "res.partner"
        remote_fields = self._remote_fields(
            models_proxy, db, uid, password, remote_model
        )

        vat = partner.vat or False
        rif = getattr(partner, "rif", False) or False
        identification_id = getattr(partner, "identification_id", False) or False

        # --- 1) BUSCAR ---
        search_value = vat or rif or identification_id
        if not search_value:
            raise UserError(
                _("El partner '%s' no tiene VAT/RIF/Identification ID.") % partner.name
            )

        # intenta con los 3 campos si existen
        search_fields = [
            f for f in ["vat", "rif", "identification_id"] if f in remote_fields
        ]
        remote_id = None
        if search_fields:
            # arma dominio OR plano
            domain = []
            for i in range(len(search_fields) - 1):
                domain.append("|")
            for f in search_fields:
                domain.append((f, "=", search_value))

            ids = models_proxy.execute_kw(
                db, uid, password, remote_model, "search", [domain], {"limit": 1}
            )
            if ids:
                return ids[0]

        # --- 2) CREAR ---
        def find_remote_id(model, field, value):
            if not value:
                return False
            rid = models_proxy.execute_kw(
                db,
                uid,
                password,
                model,
                "search",
                [[(field, "=", value)]],
                {"limit": 1},
            )
            return rid[0] if rid else False

        def find_remote_ids(model, field, values):
            if not values:
                return []
            rids = models_proxy.execute_kw(
                db, uid, password, model, "search", [[(field, "in", values)]]
            )
            return rids or []

        # country_id por código país si existe, si no por nombre
        country_remote_id = False
        if partner.country_id:
            country_remote_id = find_remote_id(
                "res.country", "code", partner.country_id.code
            ) or find_remote_id("res.country", "name", partner.country_id.name)

        # category_id (tags partner) por nombre
        cat_names = partner.category_id.mapped("name") if partner.category_id else []
        category_remote_ids = find_remote_ids("res.partner.category", "name", cat_names)

        # diarios/cuentas M2O por código o nombre (si no se consigue, se omite)
        purchase_journal_id = False
        if getattr(partner, "purchase_journal_id", False):
            purchase_journal_id = find_remote_id(
                "account.journal", "code", partner.purchase_journal_id.code
            ) or find_remote_id(
                "account.journal", "name", partner.purchase_journal_id.name
            )

        purchase_sales_id = False
        if getattr(partner, "purchase_sales_id", False):
            purchase_sales_id = find_remote_id(
                "account.journal", "code", partner.purchase_sales_id.code
            ) or find_remote_id(
                "account.journal", "name", partner.purchase_sales_id.name
            )

        purchase_islr_journal_id = False
        if getattr(partner, "purchase_islr_journal_id", False):
            purchase_islr_journal_id = find_remote_id(
                "account.journal", "code", partner.purchase_islr_journal_id.code
            ) or find_remote_id(
                "account.journal", "name", partner.purchase_islr_journal_id.name
            )

        sale_islr_journal_id = False
        if getattr(partner, "sale_islr_journal_id", False):
            sale_islr_journal_id = find_remote_id(
                "account.journal", "code", partner.sale_islr_journal_id.code
            ) or find_remote_id(
                "account.journal", "name", partner.sale_islr_journal_id.name
            )

        receivable_id = False
        if partner.property_account_receivable_id:
            receivable_id = find_remote_id(
                "account.account", "code", partner.property_account_receivable_id.code
            )

        payable_id = False
        if partner.property_account_payable_id:
            payable_id = find_remote_id(
                "account.account", "code", partner.property_account_payable_id.code
            )

        vals = {
            "name": partner.name,
            "company_type": getattr(partner, "company_type", None),
            "rif": rif if getattr(partner, "company_type", "") == "company" else None,
            "vat": vat,
            "identification_id": (
                identification_id
                if getattr(partner, "company_type", "") != "company"
                else None
            ),
            "street": partner.street or None,
            "city": partner.city or None,
            "zip": partner.zip or None,
            "country_id": country_remote_id,
            "people_type_company": getattr(partner, "people_type_company", None),
            "phone": partner.phone or None,
            "email": partner.email or None,
            "category_id": (
                [(6, 0, category_remote_ids)] if category_remote_ids else None
            ),
            "purchase_journal_id": purchase_journal_id,
            "purchase_sales_id": purchase_sales_id,
            "purchase_islr_journal_id": purchase_islr_journal_id,
            "sale_islr_journal_id": sale_islr_journal_id,
            "property_account_receivable_id": receivable_id,
            "property_account_payable_id": payable_id,
            "vat_subjected": getattr(partner, "vat_subjected", None),
            "wh_iva_agent": getattr(partner, "wh_iva_agent", None),
            "islr_withholding_agent": getattr(partner, "islr_withholding_agent", None),
            "spn": getattr(partner, "spn", None),
            "islr_exempt": getattr(partner, "islr_exempt", None),
            "contribuyente_seniat": getattr(partner, "contribuyente_seniat", None),
        }

        vals = self._filter_remote_vals(vals, remote_fields)

        new_id = models_proxy.execute_kw(
            db, uid, password, remote_model, "create", [vals]
        )
        _logger.info("Partner creado en destino: %s (%s)", partner.name, new_id)
        return new_id
