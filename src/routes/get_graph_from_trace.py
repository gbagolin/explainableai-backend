from fastapi import APIRouter
from ..types.Trace import Trace
from ..utility.map import MAP_TRACES
import xml.etree.ElementTree as ET
from  ..xpomcp.utilities import util

router = APIRouter()


def parse_xes(xes):
    """
    Parse xes log and build data from traces
    """

    xes_tree = ET.parse(xes)
    log = xes_tree.getroot()

    visual_node = util.node_from_key(log, "visual")
    nodes = util.node_from_key(visual_node, "nodes")
    edges = util.node_from_key(visual_node, "edges")

    graph = {
        "nodes": [], 
        "edges": []
    }
    
    for node in nodes: 
        tmp_node = {}
        node_key = node.attrib['key']
        tmp_node['id'] = node_key
        # print(node_key)
        for element in node: 
            # print(element.attrib)
            key = element.attrib['key']
            value = element.attrib['value']
            tmp_node[key] = value
        # print(tmp_node)
        graph['nodes'].append(tmp_node)

    for edge in edges: 
        tmp_edge = {}
        for element in edge: 
            # print(element.attrib)
            key = element.attrib['key']
            value = element.attrib['value']
            tmp_edge[key] = value
        # print(tmp_node)
        graph['edges'].append(tmp_edge)

    return graph

@router.post('/api/get_graph_from_trace')
def get_graph_from_trace(trace: Trace):

    trace_file_name = MAP_TRACES[trace.name]
    trace_path = f"src/xpomcp/tracce/{trace_file_name}"

    print(trace_file_name)
    graph = parse_xes(trace_path)

    return graph
