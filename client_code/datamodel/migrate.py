import anvil.server
from anvil import BlobMedia
from .particles import ModelTypeBase
from ..tools.utils import AppEnv
from datetime import date, datetime

EXCLUDE_MIGRATION = [
    # 'Tenants',
    # 'Users',
    # 'AppAuditLogs',
    # 'AppErrorLogs',
    # 'AppGridViews',
]

default_cols = {
    'uid': 'string',
    'tenant_uid': 'string',
    'created_by': 'string',
    'created_time': 'datetime',
    'updated_by': 'string',
    'updated_time': 'datetime'
}
sample_values = {
    'string': 'AnvilFusion',
    'number': 1,
    'boolean': True,
    'date': date.today(),
    'datetime': datetime.now(),
    'simpleObject': {'key': 'value'},
    'media': BlobMedia(content_type="text/plain", content="AnvilFusion".encode(), name="anvilfusion.txt")
}


def migrate_db_schema(logger=None):
    
    models = [attr for attr in dir(AppEnv.data_models) 
              if type(getattr(AppEnv.data_models, attr)) == type 
              and issubclass(getattr(AppEnv.data_models, attr), ModelTypeBase)
              and attr not in EXCLUDE_MIGRATION]

    # for attr in dir(AppEnv.data_models):
    #     print(attr, getattr(AppEnv.data_models, attr))
    
    migration_report = []
    
    for class_name in models:
        if logger:
            logger(class_name)
        # else:
        print(class_name)
        sample_obj, sample_refs, update_log = update_model(class_name)
        
        if sample_obj:
            sample_obj.delete(audit=False)
            
        for ref in sample_refs:
            ref.delete(audit=False)
            
        migration_report.extend(update_log)
        
    for line in migration_report:
        if logger:
            logger(line)
        # else:
        print(line)


def update_model(class_name, force_update=False, self_ref=False):
    # print('update model', class_name, force_update, self_ref)
    
    update_log = []
    sample_obj = None
    sample_refs = []
    update_log.append(f'MODEL: {class_name}')
    cls = getattr(AppEnv.data_models, class_name)
    cols = anvil.server.call('check_table', cls._table_name)
    
    if cols is None:
        update_log.append(f'>>> ERROR: Create table for {class_name} model and run migrate again')
        
    else:
        table_cols = {x['name']: x['type'] for x in cols}
        class_cols = {k: cls._attributes[k].field_type.ColumnType for k in cls._attributes}
        class_cols.update({k: 'liveObject' for k in cls._relationships})
        class_cols.update(default_cols)
        
        # get columns to delete
        del_cols = {k: table_cols[k] for k in set(table_cols) - set(class_cols)}

        if del_cols:
            update_log.append(f'>>> DELETE unused columns in the table {class_name}:')
            update_log.append([k for k in del_cols.keys()])
            
        # get columns ot add
        new_cols = {k: class_cols[k] for k in set(class_cols) - set(table_cols)}

        if new_cols or force_update:
            update = True
            sample_cols = {k: n for k, n in class_cols.items() if k not in default_cols}
            sample_data = {k: sample_values[n] for k, n in sample_cols.items() if n != 'liveObject'}
            
            # add linked sample rows
            for ref_name, ref_obj in cls._relationships.items():
                # print(ref_name, ref_obj, self_ref)
                
                if self_ref is not True:
                    ref_sample, ref_refs, ref_log = update_model(ref_obj.class_name, force_update=True, self_ref=True)
                    
                    if ref_sample:
                        sample_data[ref_name] = [ref_sample] if ref_obj.with_many else ref_sample
                        sample_refs.append(ref_sample)
                        sample_refs.extend(ref_refs)
                        
                    else:
                        update = False
                        update_log.extend(ref_log)
                        
            if update:
                sample_obj = cls(**sample_data).save(audit=False)
                
    return sample_obj, sample_refs, update_log
