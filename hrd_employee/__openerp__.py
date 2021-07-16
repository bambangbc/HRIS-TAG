{
    'name': 'hrd_employee',
    'author'  :'macmour Solution',
    'category': 'Human Resources',
    'description': """
Human Resource Employee
""",    
    'depends': ['hr','hr_recruitment','hr_contract'],
    'update_xml':[
            'employee_view.xml',
            'action.xml',
            'working_Schedule.xml',
            'wizard/update_nik_view.xml',
            'contract_view.xml',
            'report/report_contract.xml',
            'report/report_contract_template.xml',
            'security/ir_rule.xml',
            ],
    'data': [],
    'installable':True,
}
