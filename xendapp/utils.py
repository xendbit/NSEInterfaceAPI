from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response


def custom_exception_handler(exc, context):

    msg = exc.detail if hasattr(exc, 'detail') else str(exc)
    status = 403 if type(exc) in [NotAuthenticated, PermissionDenied] else 400
    return Response({'detail': msg}, status=status)


BANK_CODES_CHOICES = [
('011', 'First Bank Plc'),
('014', 'Mainstreet Bank Plc'),
('023', 'CitiBank'),
('070', 'Fidelity Bank Plc'),
('050', 'Ecobank Nigeria Plc'),
('030', 'Heritage Bank Plc'),
('032', 'Union Bank of Nigeria Plc'),
('033', 'United Bank For Africa Plc'),
('232', 'Sterling Bank Plc'),
('035', 'Wema Bank Plc'),
('057', 'Zenith Bank Plc'),
('311', 'Parkway'),
('058', 'GTBank Plc'),
('214', 'First City Monument Bank Plc'),
('215', 'UnityBank Plc'),
('315', 'GTB Mobile Money'),
('082', 'Keystone Bank Plc'),
('084', 'Enterprise Bank Ltd'),
('063', 'Diamond Bank Plc'),
('044', 'Access Bank Nigeria Plc'),
('221', 'StanbicIBTC Bank Plc'),
('068', 'Standard Chartered Bank Nigeria Ltd'),
('322', 'Zenith Mobile'),
('323', 'Access Mobile'),
('401', 'ASO Savings and Loans'),
('304', 'Stanbic Mobile'),
('305', 'PAYCOM'),
('307', 'Ecobank Mobile'),
('309', 'FBN Mobile'),
('301', 'Jaiz Bank'),
('076', 'Polaris Bank'),
('101', 'Providus Bank'),
('100', 'Suntrust Bank'),
('102', 'Titan Trust Bank')
]