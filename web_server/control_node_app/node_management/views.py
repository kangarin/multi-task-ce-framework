from node_management import node_management_blue

@node_management_blue.route('/add/<string:node_ip>')
def add_node(node_ip):
    print(node_ip)
    return 'addNode'

@node_management_blue.route('/delete/<string:node_ip>')
def delete_node(node_ip):
    print(node_ip)
    return 'deleteNode'

@node_management_blue.route('/getall')
def get_all_nodes():
    return 'getAllNodes'