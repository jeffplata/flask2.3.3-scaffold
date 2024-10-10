# process_table.py

from app import db
import re
import datetime
from flask import json, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.model_classes import get_model_class, get_primary_key
from .joined_search import compound_search


"""
    Contains functions to process Vue API tables
"""

# compound_search(table, filter_fields, search_text)

def apply_filters(query, model, filters):
    filter_conditions = []
    for field, value in filters.items():
        if hasattr(model, field):
            filter_conditions.append(getattr(model, field).icontains(value))
    if filter_conditions:
        query = query.filter(db.or_(*filter_conditions))
    return query


def apply_sort(query, model, sort_by, descending):
    if sort_by and hasattr(model, sort_by):
        col = getattr(model, sort_by)
        if descending:
            col = col.desc()
        query = query.order_by(col)
    else:
        col = get_primary_key(model)
        query = query.order_by(col)
    return query


def paginate(query, start, limit):
    total_rows = query.count()
    query = query.offset(start).limit(limit)
    return query, total_rows


def delete_instance(instance):
    db.session.delete(instance)
    db.session.commit()


def get_query(table, filters, request_args):
    filter_text = request_args.get('filtertext')
    sort_by = request_args.get('sortby')
    descending = request_args.get('sortdesc') == 'true'
    start = request_args.get('start')
    limit = request_args.get('limit')

    model_class = get_model_class(table)
    # query = apply_filters(model_class.query, model_class, filters)
    query = compound_search(table, filters, filter_text)
    query = apply_sort(query, model_class, sort_by, descending)
    query, total_rows = paginate(query, start, limit)

    return query, total_rows


def transform_error_message(e,form,message):
    try:
        error_message = str(e.orig.args[1])
    except:
        raise f"Parameter 'e' is not of type Exception."
    pattern_not_null = "Column '(.+)' cannot be null"
    pattern_duplicate = "Duplicate entry '(.+)' for key '(.+)'"
    match1 = re.match(pattern_not_null, error_message)
    match2 = re.match(pattern_duplicate, error_message)
    if match1:
        field_name_display = match1.group(1).replace('_',' ').capitalize()
        form._fields[match1.group(1)].errors.append( f"'{field_name_display}' cannot be empty")
    if match2:
        parts = match2.group(2).split('.')
        field_name = parts[len(parts)-1]
        field_name_display = match2.group(2).capitalize().replace('.',' ')
        form._fields[field_name].errors.append(f"Duplicate entry '{match2.group(1)}' in {field_name_display}")
    patterns_matched = match1 or match2
    return patterns_matched, message if patterns_matched else 'Unexpected error not trapped.'


def get_row_join_data(item_instance, joins):
    join_data = {}
    if joins is None: joins = {}
    for k, v in joins.items():  # {'roles': ['id', 'name']}
        related_objects = getattr(item_instance, k)
        join_data[k] = [{attr: getattr(related_obj, attr) for attr in v} for related_obj in related_objects]
    return join_data

def get_row_link_data(item_instance, links):
    link_data = []
    if links is None: links = {}
    for link in links:
        link_data_dict = {}
        key = link.get('key')
        linked_objects = getattr(item_instance, key)
        totalRows = len(linked_objects)
        linked_objects = linked_objects[:1]
        linked_columns = link.get('fields')
        link_data_dict[key] = [{attr: getattr(linked_obj, attr) for attr in linked_columns} for linked_obj in linked_objects]
        link_data.append(link_data_dict)
        # update links, set totalRows
        if not 'totalRows' in link:
            link['totalRows'] = []
        link['totalRows'].append(totalRows)
    return link_data


def get_row_data(item_instance, field_names, joins, links):
    ## update to include joins in data
    if joins is None: joins = {}
    if links is None: links = {}
    data = []

    # col_data = {f: getattr(item_instance, f) for f in field_names}
    
    # Dates must be formatted to yyyy-mm-dd, the ISO-8601 standard for date format
    col_data = {}
    for f in field_names:
        col_type = type(getattr(item_instance,f))
        if col_type is datetime.datetime:
            value = getattr(item_instance, f).strftime('%Y-%m-%d')
        else:
            value = getattr(item_instance, f)
        col_data[f] = value

    join_data = get_row_join_data(item_instance, joins)
    link_data = get_row_link_data(item_instance, links)
    # data = {**col_data, **join_data, **link_data}
    # the following change accomodates the new compound structure of link_data
    data = {**col_data, **join_data}
    # for d in link_data:
    #     data.update(d)
    return data


def edit_item(data, **kwargs):
    action = kwargs.get('action')
    form_class = kwargs.get('form_class')
    model_class = kwargs.get('model_class')
    # item_instance = kwargs.get('item_instance')
    # before_commit_callback = kwargs.get('before_commit_callback')
    
    message = 'Please correct errors in the form.'

    form = form_class(**data)
    if form.validate():
        try:
            # the item instance can be defined at the calling item edit (xxx_edit) function
            # ... or generically built in this function if None is passed
            if action not in ['new', 'edit']:
                raise ValueError('Unknown action.')
            if action == 'new':
                item_instance = model_class(**data)
                item_instance.id = None
                db.session.add(item_instance)
            elif action == 'edit':
                item_instance = model_class.query.get(int(data['id']))
                [setattr(item_instance, f.name, f.data) for f in form]

            db.session.commit()

            fields = kwargs.get('fields')
            fn = [f if isinstance(f, str) else f['key'] for f in fields]

            # deal with joins
            joins = kwargs.get('joins')
            if joins:
                join_names = [k for k,v in joins.items()]
                join_ids_to_delete = {}
                join_ids_to_add = {}
                current_join_ids = {}
                current_joined_data = get_row_join_data(item_instance, joins)
                for relkey, list_values in current_joined_data.items():
                    current_join_ids[relkey] = []
                    for a_dict in list_values:
                        current_join_ids.get(relkey).append(a_dict['id'])
                form_join_ids = {}
                for jn in join_names:
                    form_join_ids[jn] = []
                    form_join_data = json.loads(data.get(jn, '[]'))
                    form_join_ids.get(jn).extend(item.get('id') for item in form_join_data)

                    join_ids_to_delete = list(set(current_join_ids.get(jn)) - set(form_join_ids.get(jn)))
                    join_ids_to_add = list(set(form_join_ids.get(jn)) - set(current_join_ids.get(jn)))

                    join_model_class = getattr(model_class, jn).property.mapper.class_
                    join_data_list = join_model_class.query.all()
                    related_object = getattr(item_instance, jn)
                    for id in join_ids_to_delete:
                        join_data = [next((d for d in join_data_list if d.id==id), None)]
                        for jd in join_data:
                            related_object.remove(jd)
                        db.session.commit()
                    for i in join_ids_to_add:
                        join_data = [next((d for d in join_data_list if d.id==i), None)]
                        related_object.extend(join_data)
                        db.session.commit()
            links = kwargs.get('links')
            data = get_row_data(item_instance, fn, joins, links)
            
            return jsonify({'result': 'ok', 'newId': item_instance.id, 'data':data})
            # return jsonify({'fieldnames':fields,'data':data,'totalrows':total_rows,
            #                 'display':display,'links':links})
        
        except IntegrityError as e:
            db.session.rollback()
            _, message = transform_error_message(e,form,message)
            return jsonify({'result': 'failed', 'errors': form.errors, 'message': message})
        except Exception as e:
            db.session.rollback()
            return jsonify({'result': 'failed', 'errors': form.errors, 'message': e.args[0]})        
    return jsonify({'result': 'failed', 'errors': form.errors, 'message': message})


def delete_item(model_class, item_id, **kwargs):
    prevent_delete_callback = kwargs.get('prevent_delete_callback')
    delete_exception_callback = kwargs.get('delete_exception_callback')

    item = model_class.query.get(item_id)
    if item:
        try:
            # prevent_delete_callback must return True to abort delete
            if prevent_delete_callback:
                isAbort, message = prevent_delete_callback(item)
                if isAbort:
                    message = 'You are not allowed to delete this record.' if message == '' else message
                    return jsonify({'result': 'failed', 'message': message})
            db.session.delete(item)
            db.session.commit()
            return jsonify({'result': 'ok'})
        except IntegrityError as e:
            db.session.rollback()
            message = 'This record is in use. Deletion is not allowed.'
            return jsonify({'result': 'failed', 'message': message})
        except Exception as e:
            db.session.rollback()
            message = 'This record cannot be deleted.'
            if delete_exception_callback:
                # send back error message from the callback
                message = delete_exception_callback(e) or message
            return jsonify({'result': 'failed', 'message': message})
    return jsonify({'result': 'failed', 'message': 'Record not found.'})

def process_table(table, action=None, id=None, **kwargs):
    if request.method == 'GET' and action == 'init':
        return jsonify(kwargs.get('init_data'))
    
    model_class = get_model_class(table)
    if request.method == 'GET':
        # get table data
        try:
            filters = kwargs.get('filters')
            fields = kwargs.get('fields')
            links = kwargs.get('links')
            display = kwargs.get('display')
            joins = kwargs.get('joins', {})
            links = kwargs.get('links', {})
            # if isinstance(filters, list):
            #     filters = {i:request.args.get('filtertext') for i in filters}
            # query, total_rows = get_query(model_class, filters, request.args)
            query, total_rows = get_query(table, filters, request.args)
            fn = [f if isinstance(f, str) else f['key'] for f in fields]
            data = []
            for l in links:
                l['totalRows'] = []
            for r in query:
                data.append(get_row_data(r, fn, joins, links))
            return jsonify({'fieldnames':fields,'data':data,'totalrows':total_rows,
                            'display':display,'links':links})
        except Exception as e:
            raise e
        
    elif request.method == 'POST':
        if action=='new':
            data = request.json
            # item_instance = model_class(**data)
            # item_instance.id = None
            # before_insert_callback = kwargs.get('before_insert_callback')
            # if before_insert_callback:
            #     before_insert_callback(item_instance,data)

            return edit_item(data,
                             action='new',
                             form_class=kwargs.get('form_class'),
                             model_class=model_class,
                             #   item_instance=item_instance,
                             fields=kwargs.get('fields'),
                             joins=kwargs.get('joins'),
                             links=kwargs.get('links'),
                            )

        elif action=='edit':
            if id is None:
                raise ValueError('ID must be specified for [process_table: edit].')
            data = request.json
            # item_instance = model_class.query.filter_by(id=id).first()
            # [setattr(item_instance, k, v) for k, v in data.items()]
            
            return edit_item(data,
                             action='edit',
                             form_class=kwargs.get('form_class'),
                             model_class=model_class,
                            #  item_instance=item_instance,
                             fields=kwargs.get('fields'),
                             joins=kwargs.get('joins'),
                             links=kwargs.get('links'),
                            )
            
        elif action=='delete':
            if id is None:
                raise ValueError('ID must be specified for [process_table: delete].')
            item_instance = model_class.query.filter_by(id=id).first()
            db.session.delete(item_instance)
            try:
                db.session.commit()
                return jsonify({'result':'ok'})
            except IntegrityError:
                return jsonify({'result': 'failed', 'message': 'Delete not allowed. Record is currently in use.'})
            except Exception as e:
                return jsonify({'result': 'failed', 'message': str(e.args[0])})
