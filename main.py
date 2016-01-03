import vk



token = '6a969bea1a2f94d877bdfd2cc6aed7f29abe664f68ab3d4d714b2b3efd570c08beb5633b4c4cf8b50f07e';
session = vk.Session(token)
vk_api =  vk.API(session)
t =  vk_api.users.search(q="Красуцкий Алексей",
                         country=2)
print(t)

print(t[1]["uid"])



"""
vk_url = "https://oauth.vk.com/access_token"
params ={'client_id' : '5201271',
         'client_secret' : 'K3K1FM54yW6eIEAWvQnc',
         'redirect_uri' : 'edu-books.pp.ua',
         'code': 'ed7820860eb94a3758'}
params = urllib.parse.urlencode(params)
full_url = vk_url + "?" + params
data = urllib.request.urlopen(full_url)
print(data.read())
"""