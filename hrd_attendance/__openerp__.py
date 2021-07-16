{
    'name': 'HRD Attendance',
    'author'  :'macmour solution',
    'category': 'Human Resources',
    'description': """
Import tool untuk kehadiran karyawan dari data fingerprint berdasarkan
Fingerprint ID karyawan
""",    
    'depends': ['hr_attendance','hrd_employee'],
    'update_xml':[
        'hrd_attendance.xml',
        'wizard/report_wizard_view.xml',
        'view_report.xml',
        'report_rekap_absen.xml',
        'report/print_rekap_absen.xml'],
    'data': [],
    'installable':True,
}
