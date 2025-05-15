from typing import List, Set, Dict
from app.models.graph import Graph, Edge

class GraphValidationError(Exception):
    """Базовий клас для помилок валідації графа"""
    pass

class GraphNotConnectedError(GraphValidationError):
    """Граф не є зв'язним"""
    pass

class InvalidEdgeWeightError(GraphValidationError):
    """Невалідна вага ребра"""
    pass

class DuplicateEdgeError(GraphValidationError):
    """Дублікат ребра"""
    pass

class InvalidNodeError(GraphValidationError):
    """Невалідна вершина"""
    pass

def validate_graph(graph: Graph) -> None:
    """
    Валідація графа:
    1. Перевірка зв'язності
    2. Перевірка ваг ребер
    3. Перевірка на дублікати ребер
    4. Перевірка валідності вершин
    """
    # Перевірка валідності вершин
    validate_nodes(graph)
    
    # Перевірка ребер
    validate_edges(graph)
    
    # Перевірка зв'язності
    if not is_graph_connected(graph):
        raise GraphNotConnectedError("Граф повинен бути зв'язним")

def validate_nodes(graph: Graph) -> None:
    """
    Перевірка валідності вершин графа.
    """
    # Перевірка на дублікати вершин
    if len(graph.nodes) != len(set(graph.nodes)):
        raise InvalidNodeError("Граф містить дублікати вершин")
    
    # Перевірка на від'ємні вершини
    if any(node < 0 for node in graph.nodes):
        raise InvalidNodeError("Вершини не можуть бути від'ємними")
    
    # Перевірка на послідовність вершин
    expected_nodes = set(range(len(graph.nodes)))
    if set(graph.nodes) != expected_nodes:
        raise InvalidNodeError(
            f"Вершини повинні бути послідовними числами від 0 до {len(graph.nodes)-1}"
        )

def validate_edges(graph: Graph) -> None:
    """
    Перевірка валідності ребер графа.
    """
    seen_edges: Set[tuple] = set()
    
    for edge in graph.edges:
        # Перевірка валідності вершин ребра
        if edge.from_node not in graph.nodes or edge.to_node not in graph.nodes:
            raise InvalidNodeError(
                f"Ребро {edge.from_node}->{edge.to_node} містить невалідну вершину"
            )
        
        # Перевірка ваги ребра
        if edge.weight <= 0:
            raise InvalidEdgeWeightError(
                f"Вага ребра {edge.from_node}->{edge.to_node} повинна бути додатньою"
            )
        
        # Перевірка на дублікати ребер
        edge_key = (edge.from_node, edge.to_node)
        if edge_key in seen_edges:
            raise DuplicateEdgeError(
                f"Ребро {edge.from_node}->{edge.to_node} дублюється"
            )
        seen_edges.add(edge_key)

def is_graph_connected(graph: Graph) -> bool:
    """
    Перевірка зв'язності графа за допомогою BFS.
    """
    if not graph.nodes:
        return True
    
    # Створюємо список суміжності
    adjacency_list: Dict[int, List[int]] = {node: [] for node in graph.nodes}
    for edge in graph.edges:
        adjacency_list[edge.from_node].append(edge.to_node)
        adjacency_list[edge.to_node].append(edge.from_node)
    
    # BFS для перевірки зв'язності
    visited: Set[int] = set()
    queue: List[int] = [graph.nodes[0]]
    
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            queue.extend(neighbor for neighbor in adjacency_list[node] if neighbor not in visited)
    
    return len(visited) == len(graph.nodes) 