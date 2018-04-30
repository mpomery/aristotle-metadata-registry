from aristotle_mdr_graphql.types import AristotleObjectType

def type_from_model(meta_model):

    modelname = meta_model.__name__
    new_modelname = modelname + 'Node'

    meta_class = type('Meta', (object, ), dict(model=meta_model))
    dynamic_class = type(new_modelname, (AristotleObjectType, ), dict(Meta=meta_class))
    return dynamic_class
