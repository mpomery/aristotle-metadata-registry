import os

HAYSTACK_CONNECTIONS = {
    'default': {
        #'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'ENGINE': 'aristotle_mdr.contrib.search_backends.facetted_whoosh.FixedWhooshEngine',
        'PATH': os.path.join(os.environ.get('TOXDIR'), 'whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}
