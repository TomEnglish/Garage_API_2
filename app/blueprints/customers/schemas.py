from app.extensions import ma
from app.models import Customer



#SCHEMAS
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer #using the SQLAlchemy model to create fields used in serialization, deserialization, and validation
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True) 
login_schema = CustomerSchema(exclude=['name','phone'])