from app.extensions import ma
from app.models import Inventory
from marshmallow import fields



#SCHEMAS
class InventorySchema(ma.SQLAlchemyAutoSchema):
    price = fields.Decimal(as_string=True, places=2)
    class Meta:
        model = Inventory #using the SQLAlchemy model to create fields used in serialization, deserialization, and validation
    
inventory_item_schema = InventorySchema()
inventory_schema = InventorySchema(many=True)