import logging
_logger = logging.getLogger(__name__)

class CustomReport(models.AbstractModel):
    _name = 'report.sale_package_label.report_template_id'

    @api.multi
    def render_html(self, data=None):
        _logger.info("RUNNING REPORT")
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('your_addon.report_template_id')
        docs = self.env['your_addon.your_model'].search([('something','=','something')])   
        docargs = {
            'doc_model': report.model,
            'docs': docs,
        }
        return report_obj.render('your_addon.report_template_id', docargs)