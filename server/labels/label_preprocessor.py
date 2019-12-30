import pathlib
import json

from treelib import Node, Tree

FILE_PATH = pathlib.Path(__file__).parent
NODES_PATH = FILE_PATH.joinpath('nodes')

def load_label_tree():
    json_obj_list = {}
    for node in NODES_PATH.glob('**/*.json'):
        class_name = node.stem.replace('-', ' ')
        with open(node, 'r') as node_file:
            try:
                json_obj_list[class_name] = json.loads(node_file.read())
            except:
               pass
    return json_obj_list

def build_raw_tree():
    tree = Tree()
    tree.create_node('Object', 'root')

    loaded_tree = load_label_tree()

    emplaced_class_list = []
    inserted_classes = {}

    for label_class, config in loaded_tree.items():
        if 'parent' not in config:
            tree.create_node(label_class, label_class, parent='root', data=config)
            inserted_classes[label_class] = ''
            continue

        parent = config['parent']

        if parent in inserted_classes:
            tree.create_node(label_class, label_class, parent=parent, data=config)
            inserted_classes[label_class] = ''
        else:
            emplaced_class_list.append((parent, label_class, config))

    scan_index = 0
    scan_progress = False

    while len(emplaced_class_list) > 0:
        parent, label_class, config = emplaced_class_list[scan_index]
        if parent in inserted_classes:
            tree.create_node(label_class, label_class, parent=parent, data=config)
            inserted_classes[label_class] = ''
            del emplaced_class_list[scan_index]
            scan_progress = True
        
        if scan_index >= len(emplaced_class_list) - 1:
            if not scan_progress:
                bad_labels = [str(parent) + ',' + str(label) for (parent,label,_) in emplaced_class_list]
                raise Exception('[CONFIG_ERROR] - Invalid parents: ' + str(bad_labels))
            scan_index = 0
            scan_progress = False
        else:
            scan_index += 1

    return tree

def build_primary_tree():
    raw_tree = build_raw_tree()

    def inherit(node, field, parent_node):
        if None in (node, parent_node, parent_node.data):
            return

        if field is None:
            for k,v in parent_node.data.items():
                if k not in node.data:
                    node.data[k] = v
            if parent_node.bpointer is not None:
                inherit(node, field, raw_tree.get_node(parent_node.bpointer))
            return

        if field in parent_node.data:
            node.data[field] = parent_node.data[field]
        elif parent_node.bpointer is not None:
            inherit(node, field, raw_tree.get_node(parent_node.bpointer))

    tree = Tree()
    dynamic_properties = ['inherit']

    for node in raw_tree.all_nodes():
        raw_data = {k:v for (k,v) in node.data.items() if k not in dynamic_properties} if node.data else {}
        dynamic_map = {k:v for (k,v) in node.data.items() if k in dynamic_properties} if node.data else {}
    
        gen_node = tree.create_node(tag=node.tag, identifier=node.identifier, parent=node.bpointer, data=raw_data)

        if raw_data is None:
            continue

        if 'inherit' in dynamic_map:
            inherit_behavior = dynamic_map['inherit']
            if type(inherit_behavior) is list:
                for inherit_field in inherit_behavior:
                    inherit(gen_node, inherit_field, tree.get_node(gen_node.bpointer))
            elif type(inherit_behavior) is str and inherit_behavior == 'all':
                inherit(gen_node, None, tree.get_node(gen_node.bpointer))

    return tree