{
    'name': 'HRD Holidays',
    'author'  :'macmour',
    'category': 'Human Resources',
    'description': """
View Sakit/Izin
""",    
    'depends': ['hr_holidays'],
    'update_xml':[
    	'holiday.xml',
        'security/group.xml',
        'leave_confirm.xml',
        #'security/ir_rule.xml',
        ],
    'data': [],
    'installable':True,
}
