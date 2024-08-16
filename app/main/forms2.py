from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import StringField, BooleanField, DecimalField, SelectField, \
    DateField
from wtforms.validators import DataRequired
from app.models2 import Commodity, Region, Branch, Container, Variety, Warehouse
from app.models import User
from wtforms import SubmitField
from wtforms.validators import Optional
from wtforms.fields import DateField as WTFormsDateField
from datetime import datetime


class CommodityForm(FlaskForm):
    name = StringField('Commodity name', validators=[DataRequired()])
    description = StringField('Description')
    is_cereal = StringField('Cereal?')


class ContainerForm(FlaskForm):
    name = StringField('Container name', validators=[DataRequired()])
    description = StringField('Description')
    weight = DecimalField('Weight')
    wt_capacity = DecimalField('Weight Capacity')


class VarietyForm(FlaskForm):
    name = StringField('Variety name', validators=[DataRequired()])
    description = StringField('Description')
    commodity_id = SelectField('Commodity', choices=[])

    def __init__(self, *args, **kwargs):
        super(VarietyForm, self).__init__(*args, **kwargs)
        self.commodity_id.choices = self.get_commodities()

    @staticmethod
    def get_commodities():
        return [(c.id, c.name) for c in Commodity.query.all()]
    

class RegionForm(FlaskForm):
    name = StringField('Region name', validators=[DataRequired()])
    description = StringField('Description')


class BranchForm(FlaskForm):
    name = StringField('Branch name', validators=[DataRequired()])
    region_id = SelectField('Region', choices=[])

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        self.region_id.choices = self.get_regions()

    @staticmethod
    def get_regions():
        return [(c.id, c.name) for c in Region.query.all()]
    

class ProvinceForm(FlaskForm):
    name = StringField('Province name', validators=[DataRequired()])
    branch_id = SelectField('Branch', choices=[])

    def __init__(self, *args, **kwargs):
        super(ProvinceForm, self).__init__(*args, **kwargs)
        self.branch_id.choices = self.get_branches()

    @staticmethod
    def get_branches():
        return [(c.id, c.name) for c in Branch.query.all()]


class WarehouseForm(FlaskForm):
    name = StringField('Warehouse name', validators=[DataRequired()])
    location = StringField('Description')
    branch_id = SelectField('Branch', choices=[])

    def __init__(self, *args, **kwargs):
        super(WarehouseForm, self).__init__(*args, **kwargs)
        self.branch_id.choices = self.get_branches()

    @staticmethod
    def get_branches():
        return [(c.id, c.name) for c in Branch.query.all()]


class ItemForm(FlaskForm):
    name = StringField('Item name', validators=[DataRequired()])
    container_id = SelectField('Container', choices=[])
    variety_id = SelectField('Variety', choices=[])

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.container_id.choices = self.get_containers()
        self.variety_id.choices = self.get_varieties()

    @staticmethod
    def get_containers():
        return [(c.id, c.name) for c in Container.query.all()]

    @staticmethod
    def get_varieties():
        return [(c.id, c.name) for c in Variety.query.all()]


class ActivityForm(FlaskForm):
    name = StringField('Activity name', validators=[DataRequired()])

class OptionalDateField(WTFormsDateField):
    """Native WTForms DateField throws error for empty dates.
    Let's fix this so that we could have DateField nullable.
    
    This will be used when expected to work with JSON from a frontend,
    such as Javascript.
    """
    
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist).strip()
            if date_str == '' or date_str.lower() == 'null':
                self.data = None
                return
            try:
                if isinstance(self.format, list):
                    self.format = self.format[0]
                self.data = datetime.strptime(date_str, self.format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))

class AccountabilityForm(FlaskForm):
    name = StringField('Accountability name', validators=[DataRequired()])
    ws_id = SelectField('Warehouse supervisor', choices=[])
    wh_id = SelectField('Warehouse', choices=[])
    
    period_start = DateField('Period start')
    period_end = OptionalDateField('Period end')

    def __init__(self, *args, **kwargs):
        super(AccountabilityForm, self).__init__(*args, **kwargs)
        self.ws_id.choices = self.get_warehouse_supervisors()
        self.wh_id.choices = self.get_warehouses()

    @staticmethod
    def get_warehouse_supervisors():
        # return [(c.id, c.username) for c in User.query.order_by(User.username).all()]
        return [(c.id, c.display_name) for c in User.query.order_by(User.username).all()]

    @staticmethod
    def get_warehouses():
        return [(c.id, c.name) for c in Warehouse.query.all()]
    