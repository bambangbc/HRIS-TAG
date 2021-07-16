{
    'name': 'HRD Mutasi Karyawan',
    'author'  :'macmour solution',
    'category': 'Human Resources',
    'description': """
View Sakit/Izin
""",    
    'depends': ['hr_holidays'],
    'update_xml':[
    	'mutasi_view.xml',
        'mutasi_workflow.xml',
        'report/report_mutasi_view.xml',
        'report/report_penugasan_view.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        ],
    'data': [],
    'installable':True,
}
