from app.extensions import ma
from app.models import Mechanics



#SCHEMAS
class MechanicsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics #using the SQLAlchemy model to create fields used in serialization, deserialization, and validation
    
mechanic_schema = MechanicsSchema()
mechanics_schema = MechanicsSchema(many=True) 