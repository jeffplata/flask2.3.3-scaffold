from flask import request, jsonify
from app.api import api_bp
from app.api.routes import get_query, edit_item, delete_item
from app.models2 import Commodity, Container, Variety
from app.main.forms2 import CommodityForm, ContainerForm, VarietyForm

# commodity management
# ===============

@api_bp.route("/commodities_init")
def commodities_init():
    data = {'title': 'commodity|commodities', 'name_field': 'name'}
    return data


@api_bp.route("/commodities")
def commodities():
    filters = {'name': request.args.get('filtertext')}
    fieldnames = ['id', {'key':'name', 'sortable': 'true'}, {'key':'is_cereal','sortable':'true'}]
    query, total_rows = get_query(Commodity, filters, request.args)
    data = [{'id': r.id, 'name': r.name, 'is_cereal': r.is_cereal} for r in query]
    display = {'is_cereal': '(v) => String(v) == "true" ? "yes" : "no"'}
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows, 'display': display})


@api_bp.route("/commodity_edit", methods=['POST'])
def commodity_edit():
    data = request.json
    if data['id'] != '-1':
        commodity = Commodity.query.get(int(data['id']))
    return edit_item(data, 
                     form_class=CommodityForm, 
                     model_class=Commodity,
                     item_instance=commodity)


# def commodity_prevent_delete_callback(commodity):
#     if commodity.varieties.all():
#         return True, 'This commodity is in use. Deletion is not allowed.'
#     return False, ''


@api_bp.route("/commodity_delete", methods=['POST'])
def commodity_delete():
    item_id = request.args.get('id')
    return delete_item(Commodity, item_id)

# ====================
# Containers

@api_bp.route("/containers_init")
def containers_init():
    data = {'title': 'container|containers', 'name_field': 'name'}
    return data


@api_bp.route("/containers")
def containers():
    filters = {'name': request.args.get('filtertext'), 'description': request.args.get('filtertext')}
    fieldnames = ['id', 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'description','sortable':'true'},
                  {'key':'weight','sortable':'true'},
                  {'key':'wt_capacity','sortable':'true'},
                 ]
    query, total_rows = get_query(Container, filters, request.args)
    data = [{'id': r.id, 'name': r.name, 'description': r.description, 'weight': r.weight, 'wt_capacity':r.wt_capacity} for r in query]
    # display = {'is_cereal': '(v) => String(v) == "true" ? "yes" : "no"'}
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows})


@api_bp.route("/container_edit", methods=['POST'])
def container_edit():
    data = request.json
    return edit_item(data, 
                     form_class=ContainerForm, 
                     model_class=Container)


# ====================
# Variety

@api_bp.route("/varieties_init")
def varieties_init():
    data = {'title': 'variety|varieties', 'name_field': 'name'}
    return data


@api_bp.route("/varieties")
def varieties():
    filters = {'name': request.args.get('filtertext'), 'description': request.args.get('filtertext')}
    fieldnames = ['id', 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'description','sortable':'true'},
                  {'key':'commodity_id','sortable':'true'},
                 ]
    query, total_rows = get_query(Variety, filters, request.args)
    data = [{'id': r.id, 'name': r.name, 'description': r.description, 'commodity_id':r.commodity_id} for r in query]
    # display = {'is_cereal': '(v) => String(v) == "true" ? "yes" : "no"'}
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows})


@api_bp.route("/variety_edit", methods=['POST'])
def variety_edit():
    data = request.json
    return edit_item(data, 
                     form_class=VarietyForm, 
                     model_class=Variety)
