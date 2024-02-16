from decouple import config
ENV = config('SITE_ENV', 'dev')

print(f"========== {ENV} =================")

if ENV == 'prod' or ENV == 'beta':
    from .prod import *

elif ENV == 'dev' or ENV == 'staging':
    from .dev import *

