# import json
# import phonenumbers 
# from phonenumbers import geocoder, carrier, timezone


# def get_number_info(number):
#     number = phonenumbers.parse(number)
#     info = {}
#     info['Country'] = geocoder.description_for_number(number, 'en')
#     info['Carrier'] = carrier.name_for_number(number, 'en')
#     info['Timezone'] = timezone.time_zones_for_number(number)
#     return json.dumps(info)
# print(get_number_info('+917762980068'))


from SmartApi import SmartConnect
import pyotp
api_key='EahG0l7x'
clientId="A1307953"
pwd="6548"
token="T4LOC5ELOLLJIFN3RI3FCUYMQY"
smartApi=SmartConnect(api_key=api_key)
totp=pyotp.TOTP(token).now()
correlation_id='abc123'
data = smartApi.generateSession(clientId, pwd, totp)
authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']
feedToken = smartApi.getfeedToken()
res = smartApi.getProfile(refreshToken)
smartApi.generateToken(refreshToken)
res=res['data']['exchanges']
print(res)