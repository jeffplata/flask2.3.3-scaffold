from app.main import bp
from flask import render_template
from app.common import access_required
from app.main.forms2 import CommodityForm, ContainerForm, VarietyForm, \
    RegionForm, BranchForm, ProvinceForm, WarehouseForm, ItemForm, \
    ActivityForm, AccountabilityForm


@bp.route('/commodities')
@access_required(['admin', 'bo-admin'])
def commodities():
    form = CommodityForm()
    return render_template('commodities_vue.html', form=form)


@bp.route('/containers')
@access_required(['admin', 'bo-admin'])
def containers():
    form = ContainerForm()
    return render_template('containers_vue.html', form=form)


@bp.route('/varieties')
@access_required(['admin', 'bo-admin'])
def varieties():
    form = VarietyForm()
    return render_template('varieties_vue.html', form=form)


@bp.route('/items')
@access_required(['admin', 'bo-admin'])
def items():
    form = ItemForm()
    return render_template('items_vue.html', form=form, title='Items')


@bp.route('/activities')
@access_required(['admin', 'bo-admin'])
def activities():
    form = ActivityForm()
    return render_template('activities_vue.html', form=form, title='Activities')


@bp.route('/regions')
@access_required(['admin', 'bo-admin'])
def regions():
    form = RegionForm()
    return render_template('regions_vue.html', form=form)


@bp.route('/branches')
@access_required(['admin', 'bo-admin'])
def branches():
    form = BranchForm()
    return render_template('branches_vue.html', form=form)


@bp.route('/provinces')
@access_required(['admin', 'bo-admin'])
def provinces():
    form = ProvinceForm()
    return render_template('provinces_vue.html', form=form, title='Provinces')


@bp.route('/warehouses')
@access_required(['admin', 'bo-admin'])
def warehouses():
    form = WarehouseForm()
    return render_template('warehouses_vue.html', form=form, title='Warehouses')


@bp.route('/accountabilities')
@access_required(['admin', 'bo-admin'])
def accountabilities():
    form = AccountabilityForm()
    return render_template('accountabilities_vue.html', form=form, title='Accountabilities')
