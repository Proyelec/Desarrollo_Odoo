from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime

class HREmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = 'Préstamos de Empleados'
    _inherit = 'mail.thread'
    _order = 'name desc'

    loan_state = [
        ('draft', 'Borrador'),
        ('request', 'Solicitar'),
        ('dep_approval', 'Aprobado por Jefe de Departamento'),
        ('hr_approval', 'Aprobado por Jefe de Recursos Humanos'),
        ('paid', 'Pagado'),
        ('done', 'Hecho'),
        ('close', 'Cerrado'),
        ('reject', 'Rechazado'),
        ('cancel', 'Cancelado')
    ]
                
    @api.model
    def _get_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    @api.model
    def _get_default_user(self):
        return self.env.user

    name = fields.Char('Nombre', default='/', copy=False)
    state = fields.Selection(loan_state, string='Estatus', default='draft', track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', default=_get_employee, required=True, string='Empleado')
    department_id = fields.Many2one('hr.department', string='Departamento')
    hr_manager_id = fields.Many2one('hr.employee', string='Jefe de Recursos Humanos')
    manager_id = fields.Many2one('hr.employee', string='Jefe de Departamento', required=True)
    job_id = fields.Many2one('hr.job', string="Cargo")
    date = fields.Date('Fecha', default=fields.Date.today())
    start_date = fields.Date('Fecha de inicio', default=fields.Date.today(), required=True)
    period = fields.Selection([('bi-weekly', 'Quincenal'), ('monthly', 'Mensual')], string='Periodo', default='monthly')
    end_date = fields.Date('Fecha fin', compute='_get_end_date')
    term = fields.Integer('Cuotas', required=True)
    loan_type_id = fields.Many2one('hr.employee.loan.type', string='Tipo de préstamo', required=True)
    payment_method = fields.Selection([('by_payslip', 'En Nómina')], string='Método de pago', default='by_payslip', required=True)
    loan_amount = fields.Monetary('Monto del préstamo', required=True, currency_field='currency_id')
    paid_amount = fields.Monetary('Monto pagado', compute='get_paid_amount', currency_field='currency_id')
    remaing_amount = fields.Monetary('Monto restante', compute='get_remaing_amount', currency_field='currency_id')
    installment_amount = fields.Monetary('Monto de cuota', required=True, compute='get_installment_amount', currency_field='currency_id')
    loan_url = fields.Char('URL', compute='get_loan_url')
    user_id = fields.Many2one('res.users', default=_get_default_user)
    is_apply_interest = fields.Boolean('Aplicar Interés', default=True)
    interest_type = fields.Selection([('liner', 'Linear'), ('reduce', 'Reducido')], string='Tipo de Interés', default='liner')
    interest_rate = fields.Float(string='% Intereses', default=10)
    interest_amount = fields.Monetary('Monto de intereses', compute='get_interest_amount', currency_field='currency_id')
    installment_lines = fields.One2many('hr.employee.loan.installment.line', 'loan_id', string='Cuotas')
    notes = fields.Text('Razón', required=True)
    is_close = fields.Boolean('Cerrado', compute='is_ready_to_close')
    move_id = fields.Many2one('account.move', string='Asiento Contable')
    loan_document_line_ids = fields.One2many('hr.employee.loan.document', 'loan_id')
    installment_count = fields.Integer(compute='get_interest_count')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Moneda', related='company_id.currency_id', readonly=True)

    @api.depends('start_date', 'term')
    def _get_end_date(self):
        for loan in self:
            loan.end_date = loan.start_date + relativedelta(months=loan.term) if loan.start_date and loan.term else False

    @api.depends('installment_lines', 'paid_amount')
    def get_extra_interest(self):
        for loan in self:
            loan.extra_in_amount = sum(line.ins_interest for line in loan.installment_lines if line.is_skip)

    @api.depends('installment_lines')
    def get_interest_count(self):
        for loan in self:
            loan.installment_count = len(loan.installment_lines)

    @api.onchange('term', 'interest_rate', 'interest_type')
    def onchange_term_interest_type(self):
        if self.loan_type_id:
            self.term = self.loan_type_id.loan_term
            self.interest_rate = self.loan_type_id.interest_rate
            self.interest_type = self.loan_type_id.interest_type
    
    @api.depends('remaing_amount')
    def is_ready_to_close(self):
        for loan in self:
            loan.is_close = loan.remaing_amount <= 0 and loan.state == 'done'

    @api.depends('installment_lines')
    def get_paid_amount(self):
        for loan in self:
            loan.paid_amount = sum(
                line.total_installment if not line.is_skip else line.ins_interest 
                for line in loan.installment_lines if line.is_paid
            )

    def compute_installment(self):
        vals = []
        date = self.start_date
        for i in range(self.term):
            if self.period == 'bi-weekly':
                if date.day <= 15:
                    date = (date + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
                    if date.day == 31:
                        date = date.replace(day=30)
                else:
                    date = date + relativedelta(months(1)).replace(day=15)
            else:
                date = date + relativedelta(months=i)

            amount = self.loan_amount
            interest_amount = 0.0
            ins_interest_amount = 0.0

            if self.is_apply_interest:
                interest_amount = (amount * self.term / (12 if self.period == 'monthly' else 24) * self.interest_rate) / 100

                if self.interest_type == 'reduce':
                    amount -= self.installment_amount * i
                    interest_amount = (amount * self.term / (12 if self.period == 'monthly' else 24) * self.interest_rate) / 100
                
                ins_interest_amount = interest_amount / self.term

            vals.append((0, 0, {
                'name': f'Cuota - {self.name} - {i + 1}',
                'employee_id': self.employee_id.id if self.employee_id else False,
                'date': date,
                'amount': amount,
                'interest': interest_amount,
                'installment_amt': self.installment_amount,
                'ins_interest': ins_interest_amount,
            }))

        self.installment_lines.unlink()
        self.installment_lines = vals


    @api.onchange('is_apply_interest')
    def _onchange_is_apply_interest(self):
        if not self.is_apply_interest:
            self.interest_rate = 0.0
    
    @api.onchange('loan_type_id', 'interest_type', 'term')
    def _onchange_loan_type(self):
        if self.loan_type_id:
            self.term = self.loan_type_id.loan_term
            self.interest_rate = self.loan_type_id.interest_rate if self.is_apply_interest else 0.0
            self.interest_type = self.loan_type_id.interest_type

    @api.depends('paid_amount', 'loan_amount', 'interest_amount')
    def get_remaing_amount(self):
        for loan in self:
            loan.remaing_amount = loan.loan_amount + loan.interest_amount - loan.paid_amount

    @api.depends('loan_amount', 'interest_rate', 'is_apply_interest', 'installment_lines')
    def get_interest_amount(self):
        for loan in self:
            if loan.is_apply_interest:
                if loan.interest_type == 'liner':
                    loan.interest_amount = (loan.loan_amount * loan.term / 12 * loan.interest_rate) / 100
                else:
                    loan.interest_amount = sum(line.ins_interest for line in loan.installment_lines)
            else:
                loan.interest_amount = 0.0


    @api.onchange('interest_type', 'interest_rate')
    def onchange_interest_rate_type(self):
        if self.loan_type_id:
            self.interest_rate = self.loan_type_id.interest_rate
            self.interest_type = self.loan_type_id.interest_type

    def get_loan_url(self):
        for loan in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if base_url:
                action_id = self.env.ref('l10n_ve_payroll_usd.action_hr_employee_loan').id
                menu_id = self.env.ref('l10n_ve_payroll_usd.menu_hr_employee_loan').id
                loan.loan_url = f'{base_url}/web#id={loan.id}&action={action_id}&model=hr.employee.loan&view_type=form&cids=&menu_id={menu_id}'

    @api.depends('term', 'loan_amount')
    def get_installment_amount(self):
        for loan in self:
            loan.installment_amount = loan.loan_amount / loan.term if loan.loan_amount and loan.term else 0

    @api.constrains('employee_id')
    def _check_loan(self):
        for loan in self:
            year = datetime.now().year
            s_date = f'{year}-01-01'
            e_date = f'{year}-12-31'

            loan_count = self.search_count([
                ('employee_id', '=', loan.employee_id.id),
                ('date', '>=', s_date),
                ('date', '<=', e_date),
            ])

            if loan_count > loan.employee_id.loan_request:
                raise ValidationError(f"Usted ya tiene {loan.employee_id.loan_request} préstamos en este año")

    @api.onchange('loan_type_id')
    def _onchange_loan_type_id(self):
        if self.loan_type_id:
            self.term = self.loan_type_id.loan_term


    @api.constrains('loan_amount', 'term', 'loan_type_id', 'employee_id.loan_request')
    def _check_loan_amount_term(self):
        for loan in self:
            if loan.loan_amount <= 0:
                raise ValidationError("El monto del préstamo debe ser mayor que 0.00")
            if loan.loan_amount > loan.loan_type_id.loan_limit:
                raise ValidationError(f"Su solicitud solo puede ser de {loan.loan_type_id.loan_limit} como máximo")
            if loan.term <= 0:
                raise ValidationError("El término del préstamo debe ser mayor que 0")
            if loan.term > loan.loan_type_id.loan_term:
                raise ValidationError(f"El término máximo del préstamo es de {loan.loan_type_id.loan_term} meses")

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.loan') or '/'
        return super(HREmployeeLoan, self).create(vals)

    def copy(self, default=None):
        default = dict(default or {}, name='/')
        return super(HREmployeeLoan, self).copy(default)

    def unlink(self):
        for loan in self:
            if loan.state != 'draft':
                raise ValidationError(_('Solo se pueden eliminar préstamos en estado borrador!'))
        return super(HREmployeeLoan, self).unlink()

    def action_view_loan_installment(self):
        action = self.env.ref('l10n_ve_payroll_usd.action_installment_line').read()[0]
        installments = self.mapped('installment_lines')

        if len(installments) > 1:
            action['domain'] = [('id', 'in', installments.ids)]
        elif installments:
            action.update({
                'views': [(self.env.ref('l10n_ve_payroll_usd.view_loan_emi_form').id, 'form')],
                'res_id': installments.id,
            })

        return action

    def action_send_request(self):
        if not self.manager_id:
            raise ValidationError(_('Por favor, seleccione el gerente de departamento !!!'))
        
        self.state = 'request'
        if not self.installment_lines:
            self.compute_installment()

        if self.manager_id.work_email:
            template_id = self.env['ir.model.data']._xmlid_lookup('l10n_ve_payroll_usd.dev_dep_manager_request')[2]
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def dep_manager_approval_loan(self):
        self.state = 'dep_approval'
        email = self.get_hr_manager_email()
        if email:
            template_id = self.env['ir.model.data']._xmlid_lookup('l10n_ve_payroll_usd.dev_hr_manager_request')[2]
            self.env['mail.template'].browse(template_id).write({'email_to': email}).send_mail(self.id, force_send=True)

    def hr_manager_approval_loan(self):
        self.state = 'hr_approval'
        self.hr_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id
        if self.employee_id.work_email:
            template_id = self.env['ir.model.data']._xmlid_lookup('l10n_ve_payroll_usd.hr_manager_confirm_loan')[2]
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def dep_manager_reject_loan(self):
        self.state = 'reject'
        if self.employee_id.work_email:
            template_id = self.env['ir.model.data']._xmlid_lookup('l10n_ve_payroll_usd.dep_manager_reject_loan')[2]
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def action_close_loan(self):
        self.state = 'close'
        if self.employee_id.work_email:
            template_id = self.env['ir.model.data']._xmlid_lookup('l10n_ve_payroll_usd.hr_manager_closed_loan')[2]
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def hr_manager_reject_loan(self):
        self.state = 'reject'
        self.hr_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id
        if self.employee_id.work_email:
            template_id = self.env['ir.model.data']._xmlid_lookup('l10n_ve_payroll_usd.hr_manager_reject_loan')[2]
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def cancel_loan(self):
        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'
        self.hr_manager_id = False

    def paid_loan(self):
        if not self.employee_id.address_home_id:
            raise ValidationError(_('Por favor, agregue la dirección del empleado !!!'))
            
        self.state = 'paid'
        credit = self.loan_amount
        interest_credit = self.interest_amount if self.interest_amount else 0
        acc_move_id = self.env['account.move'].create({
            'date': self.date,
            'ref': self.name,
            'journal_id': self.loan_type_id.journal_id.id,
            'company_id': self.env.company.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.loan_type_id.loan_account.id,
                    'partner_id': self.employee_id.address_home_id.id,
                    'name': self.name,
                    'credit': credit,
                }),
                (0, 0, {
                    'account_id': self.loan_type_id.interest_account.id,
                    'partner_id': self.employee_id.address_home_id.id,
                    'name': f'{self.name} - Interest',
                    'credit': interest_credit,
                }),
                (0, 0, {
                    'account_id': self.employee_id.address_home_id.property_account_payable_id.id,
                    'partner_id': self.employee_id.address_home_id.id,
                    'name': self.name,
                    'debit': credit + interest_credit,
                }),
            ]
        })
        self.move_id = acc_move_id.id

    def view_journal_entry(self):
        if self.move_id:
            return {
                'view_mode': 'form',
                'res_id': self.move_id.id,
                'res_model': 'account.move',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
            }
            
    def action_done_loan(self):
        self.state = 'done'

    def send_loan_detail(self):
        """Enviar un correo electrónico con detalles del préstamo al empleado."""
        for loan in self:
            if not loan.employee_id.work_email:
                raise ValidationError(_("El empleado no tiene un correo electrónico asignado."))

            # Asumimos que tienes una plantilla de correo definida para esto
            template_id = self.env.ref('l10n_ve_payroll_usd.mail_template_loan_details').id
            self.env['mail.template'].browse(template_id).send_mail(loan.id, force_send=True)

            # Registrar el hecho en el chatter
            loan.message_post(body=_("Se ha enviado el correo electrónico con los detalles del préstamo."))

