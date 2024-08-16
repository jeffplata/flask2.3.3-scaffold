from app import db
from decimal import Decimal
from sqlalchemy.ext.hybrid import hybrid_property


class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, default='')
    description = db.Column(db.String(80), default='')

    branches = db.relationship('Branch', back_populates='region', passive_deletes=True)
    
    def __repr__(self):
        return f'<Region {self.name}>'
    
    def get_warehouses(self):
        return Warehouse.query.join(Branch).filter(Branch.region_id == self.id)
    
    def get_provinces(self):
        return Province.query.join(Branch).filter(Branch.region_id == self.id)
    

class Branch(db.Model):
    __tablename__ = 'branch'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, default='')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id', ondelete='RESTRICT'))
    
    region = db.relationship('Region', back_populates='branches')
    warehouses = db.relationship('Warehouse', back_populates='branch', passive_deletes=True)
    provinces = db.relationship('Province', back_populates='branch', passive_deletes=True)

    def __repr__(self):
        return f'<Branch {self.name}>'
    
    @hybrid_property
    def region_name(self):
        return self.region.name if self.region else None
    

class Province(db.Model):
    __tablename__ = 'province'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, default='')
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id', ondelete='RESTRICT'))
    
    branch = db.relationship('Branch', back_populates='provinces')

    def __repr__(self):
        return f'<Province {self.name}>'
    
    @hybrid_property
    def branch_name(self):
        return self.branch.name if self.branch else None
    

class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, default='')
    location = db.Column(db.String(80), default='')
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id', ondelete='RESTRICT'))
    
    branch = db.relationship('Branch', back_populates='warehouses')
    accountabilities = db.relationship('Accountability', back_populates='warehouse')
    
    def __repr__(self):
        return f'<Warehouse {self.name}>'

    @hybrid_property
    def region_name(self):
        return self.branch.region.name if self.branch.region else None
    
    @hybrid_property
    def branch_name(self):
        return self.branch.name if self.branch else None


class Commodity(db.Model):
    __tablename__ = 'commodity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, default='')
    is_cereal = db.Column(db.String(5), default='false' )
    varieties = db.relationship('Variety', backref='commodity', passive_deletes=True)

    def __repr__(self):
        return f'<Commodity {self.name}>'


class Container(db.Model):
    __tablename__ = 'container'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(20), default='')
    weight = db.Column(db.Numeric(15, 4), default=Decimal('0'))
    wt_capacity = db.Column(db.Numeric(15, 4), default=Decimal('50'))

    items = db.relationship('Item', back_populates='container', passive_deletes=True)

    def __repr__(self):
        return f'<Container {self.name}>'


class Variety(db.Model):
    __tablename__ = 'variety'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, default='')
    description = db.Column(db.String(80), default='')
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id', ondelete='RESTRICT'))
    # commodity = db.relationship(
    #     "Commodity", backref=db.backref("varieties", lazy="dynamic"))

    items = db.relationship('Item', back_populates='variety', passive_deletes=True)
    
    def __repr__(self):
        return f'<Variety {self.name}>'
    
    @hybrid_property
    def commodity_name(self):
        return self.commodity.name if self.commodity else None
    

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, default='')
    container_id = db.Column(db.Integer, db.ForeignKey('container.id', ondelete='RESTRICT'))
    variety_id = db.Column(db.Integer, db.ForeignKey('variety.id', ondelete='RESTRICT'))
    # commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id', ondelete='RESTRICT'))

    variety = db.relationship('Variety', back_populates='items')
    container = db.relationship('Container', back_populates='items')

    def __repr__(self):
        return f'<Item {self.name}>'
    
    @hybrid_property
    def variety_name(self):
        return self.variety.name if self.variety else None
    
    @hybrid_property
    def commodity_name(self):
        return self.variety.commodity.name if self.variety.commodity else None
    
    @hybrid_property
    def container_name(self):
        return self.container.name if self.container else None
    

class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, default='', nullable=False)

    def __repr__(self):
        return f'<Activity {self.name}>'
    

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, default='', nullable=False)
    longname = db.Column(db.String(80), unique=True, default='', nullable=False)

    def __repr__(self):
        return f'<Document {self.name}>'


class Accountability(db.Model):
    __tablename__ = 'accountability'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, default='')
    ws_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'))
    wh_id = db.Column(db.Integer, db.ForeignKey('warehouse.id', ondelete='RESTRICT'))
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    warehouse_supervisor = db.relationship('User', back_populates='accountabilities')
    warehouse = db.relationship('Warehouse', back_populates='accountabilities')
    
    def __repr__(self):
        return f'<Accountability {self.name}>'
    
    @hybrid_property
    def warehouse_supervisor_name(self):
        # return self.warehouse_supervisor.username if self.warehouse_supervisor else None
        return self.warehouse_supervisor.display_name if self.warehouse_supervisor else None
    
    @hybrid_property
    def warehouse_name(self):
        return self.warehouse.name if self.warehouse else None
