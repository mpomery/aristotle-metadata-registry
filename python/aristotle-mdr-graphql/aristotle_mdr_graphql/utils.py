from aristotle_mdr_graphql.types import AristotleObjectType
import logging
logger = logging.getLogger(__name__)

def type_from_model(meta_model):

    modelname = meta_model.__name__
    new_modelname = modelname + 'Node'
    logger.debug(new_modelname)

    meta_class = type('Meta', (object, ), dict(model=meta_model))
    dynamic_class = type(new_modelname, (AristotleObjectType, ), dict(Meta=meta_class))
    return dynamic_class
