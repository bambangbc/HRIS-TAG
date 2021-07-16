{
    'name': 'HR Security Tag',
    'version': '1.2',
    'author': 'wawan',
    'category': 'Human Resources',
    'website': 'https://www.odoo-bandung.com',
    'summary': 'Security HR Untuk Tag',
    'description': """
        Security HR Untuk Tag
    """,
    'data': [
        'security/employee_security.xml',
        'user.xml',
        'security/ir.model.access.csv',
    ],
    'depends': ['hr','hrd_employee','hrd_attendance','base'],

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
