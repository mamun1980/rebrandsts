from decouple import config
ENV = config('SITE_ENV', 'dev')

if ENV == 'prod':
    print(f"{'*' * 10} loading {ENV} evironment settings {'*' * 10}")
    from .prod import *
elif ENV == 'beta':
    print(f"{'*' * 10} loading {ENV} evironment settings {'*' * 10}")
    from .beta import *
elif ENV == 'staging':
    print(f"{'*' * 10} loading {ENV} evironment settings {'*' * 10}")
    from .staging import *
elif ENV == 'dev':
    print(f"{'*' * 10} loading {ENV} evironment settings {'*' * 10}")
    from .dev import *