from flask import jsonify
from app.api import api_bp
from app.model_classes import get_model_class
from app.main.forms import UserForm, RoleForm
from app.main.forms2 import CommodityForm, ContainerForm, VarietyForm, \
    RegionForm, BranchForm, ProvinceForm, WarehouseForm, ItemForm, \
    ActivityForm, AccountabilityForm
from .process_table import process_table

@api_bp.route('/<string:table>', methods=['GET'])
@api_bp.route('/<string:table>/<string:action>', methods=['GET','POST'])
@api_bp.route('/<string:table>/<string:action>/<string:id>', methods=['POST','DELETE'])
def vue_table(table, action=None, id=None):
    settings = [
        {'table': 'user', 'settings':
            {
            'init_data':{'title':'user|users', 'name_field':'username'},
            'fields':['id', 
                  {'key': 'username', 'sortable': 'true'},
                  {'key': 'email', 'sortable': 'true'},
                  {'key': 'first_name', 'sortable': 'true'},
                  {'key': 'last_name', 'sortable': 'true'},
                  ],
            'joins':{'roles':['id','name']},
            'filters':['username', 'email', 'first_name', 'last_name'],
            'form_class': UserForm,
            }
        },
        {'table': 'role', 'settings':
            {
            'init_data':{'title':'role|roles', 'name_field':'name'},
            'fields':['id', {'key':'name', 'sortable': 'true'}, {'key':'description','sortable':'true'}],
            'links':[
                {'key':'users',
                 'fields':['id', 'username', 'email'],
                 'link':'role_users',
                 'placeholder': 'Select a user to add...'
                 }
            ],
            'filters':['name', 'description'],
            'form_class': RoleForm,
            }
        },
        {'table': 'commodity', 'settings':
            {
            'init_data':{'title':'commodity|commodities', 'name_field':'name'},
            'fields':['id', {'key':'name', 'sortable': 'true'}, {'key':'is_cereal','sortable':'true'}],
            'links':[
                {'key':'varieties', 
                 'fields':['id','name'], 
                 'link':'commodity_varieties',
                 'placeholder':'Select a variety to add...'}],
            'display':{'is_cereal': '(v, r) => String(v) == "true" ? "yes" : "no"'},
            'filters':['name'],
            'form_class': CommodityForm,
            }
        },
        {'table': 'container', 'settings':
            {
            'init_data':{'title':'container|containers', 'name_field':'name'},
            'fields':['id', {'key':'name', 'sortable': 'true'}, 
                      {'key':'description','sortable':'true'},
                      {'key':'weight','sortable':'true'},
                      {'key':'wt_capacity','sortable':'true'}],
            'filters':['name'],
            'form_class': ContainerForm,
            }
        },
        {'table': 'variety', 'settings':
            {
            'init_data':{'title':'variety|varieties', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'description','sortable':'true'},
                  {'key':'commodity_id','sortable':'true'},
                  {'key':'commodity_name','sortable':'false','visible':'false'},
                  ],
            'display':{'commodity_id':'(v, r) => r.commodity_name'},
            'filters':['name','description','commodity.name'],
            'form_class': VarietyForm,
            }
        },
        {'table': 'region', 'settings':
            {
            'init_data':{'title':'region|regions', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'description','sortable':'true'},
                  ],
            'filters':['name','description'],
            'form_class': RegionForm,
            }
        },
        {'table': 'branch', 'settings':
            {
            'init_data':{'title':'branch|branches', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'region_id','sortable':'true'},
                  {'key':'region_name','sortable':'true','visible':'false'},
                  ],
            'links':[
                {'key':'provinces',
                 'fields':['id', 'name'],
                 'link':'branch_provinces',
                 'placeholder': 'Select a province to add...'
                 }
            ],
            'display':{'region_id':'(v, r) => r.region_name'},
            'filters':['name','region.name'],
            'form_class': BranchForm,
            }
        },
        {'table': 'province', 'settings':
            {
            'init_data':{'title':'province|provinces', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'branch_id','sortable':'true'},
                  {'key':'branch_name','sortable':'true','visible':'false'},
                  ],
            'display':{'branch_id':'(v, r) => r.branch_name'},
            'filters':['name'],
            'form_class': ProvinceForm,
            }
        },
        {'table': 'warehouse', 'settings':
            {
            'init_data':{'title':'warehouse|warehouses', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'location', 'sortable': 'true'}, 
                  {'key':'branch_id','sortable':'true'},
                  {'key':'branch_name','sortable':'true','visible':'false'},
                  ],
            'display':{'branch_id':'(v, r) => r.branch_name'},
            'filters':['name'],
            'form_class': WarehouseForm,
            }
        },
        {'table': 'item', 'settings':
            {
            'init_data':{'title':'item|items', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'variety_id','sortable':'true'},
                  {'key':'container_id','sortable':'true'},
                  {'key':'commodity_name','sortable':'false','visible':'true'},
                  {'key':'variety_name','sortable':'true','visible':'false'},
                  {'key':'container_name','sortable':'true','visible':'false'},
                  ],
            'display':{'variety_id':'(v, r) => r.variety_name',
                       'container_id':'(v, r) => r.container_name'},
            'filters':['name'],
            'form_class': ItemForm,
            }
        },
        {'table': 'activity', 'settings':
            {
            'init_data':{'title':'activity|activities', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  ],
            'filters':['name'],
            'form_class': ActivityForm,
            }
        },
        {'table': 'accountability', 'settings':
            {
            'init_data':{'title':'accountability|accountabilities', 'name_field':'name'},
            'fields':[{'key':'id', 'sortable': 'true'}, 
                  {'key':'name', 'sortable': 'true'}, 
                  {'key':'wh_id', 'sortable': 'true'}, 
                  {'key':'ws_id', 'sortable': 'true'}, 
                  {'key':'period_start', 'sortable': 'true'}, 
                  {'key':'period_end', 'sortable': 'true'}, 
                  {'key':'warehouse_name', 'visible': 'false'}, 
                  {'key':'warehouse_supervisor_name', 'visible': 'false'}, 
                  ],
            'display': {
                'wh_id':'(v, r) => r.warehouse_name',
                'ws_id':'(v, r) => r.warehouse_supervisor_name',
            },
            'filters':['name','warehouse.name','user.display_name'],
            'form_class': AccountabilityForm,
            }
        },
    ]
    other_params = next((s['settings'] for s in settings if s['table'] == table), None)
    if other_params is None:
        return jsonify({'error': f"Invalid table name: {table}"}), 400
    return process_table(table, action, id, **other_params)
            