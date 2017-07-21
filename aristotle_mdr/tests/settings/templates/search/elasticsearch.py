HAYSTACK_CONNECTIONS = {
    'default': {
        # 'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        # 'ENGINE': 'aristotle_mdr.contrib.search_backends.elasticsearch2.Elasticsearch2SearchEngine',
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}
