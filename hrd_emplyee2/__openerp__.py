{
    'name': 'hrd_employee2',
    'author'  :'macmour Solution',
    'category': 'Human Resources',
    'description': """
Human Resource Employee
""",    
    'depends': ['hr','hrd_employee','hr_recruitment','hr_contract'],
    'update_xml':[
            'view_employee.xml',
            'report/report.xml',
            'report/evaluasi_karyawan.xml',
            'report/kartu_kerja_kasir.xml',
            ],
    'data': [],
    'installable':True,
}
