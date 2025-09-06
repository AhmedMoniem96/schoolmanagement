from odoo import fields, models, tools

class FeesStructureReport(models.Model):
    _name = 'fees.structure.report'
    _description = 'Fees Structure Report'
    _auto = False
    _rec_name = 'name'

    name = fields.Char(string="Fees Structure")
    semester_id = fields.Many2one('school.semester', string='Semester')
    academic_year_id = fields.Many2one('academic.year', string='Academic Year')
    currency_id = fields.Many2one('res.currency', string='Currency')
    activation_date = fields.Date(string="Activation Date")

    subtotal_amount = fields.Monetary(string='Subtotal', currency_field='currency_id')
    discount_amount = fields.Monetary(string='Discount', currency_field='currency_id')
    total_amount    = fields.Monetary(string='Total Amount', currency_field='currency_id')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'fees_structure_report')
        self._cr.execute("""
            CREATE VIEW fees_structure_report AS
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY fs.name, fs.semester_id, fs.academic_year_id, fs.currency_id
                )::int AS id,
                fs.name AS name,
                fs.semester_id AS semester_id,
                fs.academic_year_id AS academic_year_id,
                fs.currency_id AS currency_id,
                MIN(fs.activation_date)    AS activation_date,
                SUM(fs.subtotal_amount)    AS subtotal_amount,
                SUM(fs.discount_amount)    AS discount_amount,
                SUM(fs.total_amount)       AS total_amount
            FROM school_fee_structure fs
            GROUP BY
                fs.name, fs.semester_id, fs.academic_year_id, fs.currency_id
        """)
