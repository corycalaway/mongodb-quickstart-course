import mongoengine

alias_core = 'core'
db = 'buddies_bnb'

# data = dict(
#     username=env,
#     password=env,
#     host=env,
#     port=env,
#     authentication_source='admin',
#     authentication_mechanism='SCRAM-SHA-1',
#     ssl=True,
#     ssl_cert_reqs=ssl.CERT_NONE
# )

def global_init():
    # can have multiple databases listed here. after name add , **data
    mongoengine.register_connection(alias=alias_core, name=db)
