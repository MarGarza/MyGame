# XML Parser/Data Access Object JurassicParkTemplate.py
"""AUTO-GENERATED Source file for JurassicParkTemplate.py"""
import xml.sax
import Queue
import Q2API.xml.base_xml

rewrite_name_list = ("name", "value", "attrs", "flatten_self", "flatten_self_safe_sql_attrs", "flatten_self_to_utf8", "children")

def process_attrs(attrs):
    """Process sax attribute data into local class namespaces"""
    if attrs.getLength() == 0:
        return {}
    tmp_dict = {}
    for name in attrs.getNames():
        tmp_dict[name] = attrs.getValue(name)
    return tmp_dict

def clean_node_name(node_name):
    """handle problem characters and names for XML node name"""
    clean_name = node_name.replace(":", "_").replace("-", "_").replace(".", "_")

    if clean_name in rewrite_name_list:
        clean_name = "_" + clean_name + "_"

    return clean_name

class door_q2class(Q2API.xml.base_xml.XMLNode):
    """door : (original name) door"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'room']
        Q2API.xml.base_xml.XMLNode.__init__(self, "door", attrs, None, [])

class include_q2class(Q2API.xml.base_xml.XMLNode):
    """include : (original name) include"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'intro']
        Q2API.xml.base_xml.XMLNode.__init__(self, "include", attrs, None, [])

class interactable_q2class(Q2API.xml.base_xml.XMLNode):
    """interactable : (original name) interactable"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'room']
        self.text = []
        self.item = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "interactable", attrs, None, [])

class item_q2class(Q2API.xml.base_xml.XMLNode):
    """item : (original name) item"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'player']
        Q2API.xml.base_xml.XMLNode.__init__(self, "item", attrs, None, [])

class level_q2class(Q2API.xml.base_xml.XMLNode):
    """level : (original name) level"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'player']
        Q2API.xml.base_xml.XMLNode.__init__(self, "level", attrs, None, [])

class text_q2class(Q2API.xml.base_xml.XMLNode):
    """text : (original name) text"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'intro']
        Q2API.xml.base_xml.XMLNode.__init__(self, "text", attrs, None, [])

class treasure_q2class(Q2API.xml.base_xml.XMLNode):
    """treasure : (original name) treasure"""
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'room']
        self.item = []
        self.include = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "treasure", attrs, None, [])

class ending_q2class(Q2API.xml.base_xml.XMLNode):
    """ending : (original name) ending"""
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.text = []
        self.include = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "ending", attrs, None, [])

class enemy_q2class(Q2API.xml.base_xml.XMLNode):
    """enemy : (original name) enemy"""
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.level = []
        self.text = []
        self.include = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "enemy", attrs, None, [])

class intro_q2class(Q2API.xml.base_xml.XMLNode):
    """intro : (original name) intro"""
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.text = []
        self.include = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "intro", attrs, None, [])

class player_q2class(Q2API.xml.base_xml.XMLNode):
    """player : (original name) player"""
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.level = []
        self.text = []
        self.item = []
        self.include = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "player", attrs, None, [])

class room_q2class(Q2API.xml.base_xml.XMLNode):
    """room : (original name) room"""
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.enemy = []
        self.door = []
        self.text = []
        self.treasure = []
        self.interactable = []
        self.include = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "room", attrs, None, [])

class game_q2class(Q2API.xml.base_xml.XMLNode):
    """game : (original name) game"""
    def __init__(self, attrs):
        self.level = 1
        self.path = [None]
        self.enemy = []
        self.room = []
        self.ending = []
        self.player = []
        self.intro = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "game", attrs, None, [])

class NodeHandler(xml.sax.handler.ContentHandler):
    """SAX ContentHandler to map XML input class/object"""
    def __init__(self, return_q):     # overridden in subclass
        self.obj_depth = [None]
        self.return_q = return_q
        self.last_processed = None
        self.char_buffer = []
        xml.sax.handler.ContentHandler.__init__(self)   # superclass init

    def startElement(self, name, attrs): # creating the node along the path being tracked
        """Override base class ContentHandler method"""
        name = clean_node_name(name)
        p_attrs = process_attrs(attrs)

        if name == "":
            raise ValueError("XML Node name cannot be empty")

        elif name == "enemy":
            self.obj_depth.append(enemy_q2class(p_attrs))

        elif name == "door":
            self.obj_depth.append(door_q2class(p_attrs))

        elif name == "room":
            self.obj_depth.append(room_q2class(p_attrs))

        elif name == "level":
            self.obj_depth.append(level_q2class(p_attrs))

        elif name == "text":
            self.obj_depth.append(text_q2class(p_attrs))

        elif name == "treasure":
            self.obj_depth.append(treasure_q2class(p_attrs))

        elif name == "interactable":
            self.obj_depth.append(interactable_q2class(p_attrs))

        elif name == "ending":
            self.obj_depth.append(ending_q2class(p_attrs))

        elif name == "player":
            self.obj_depth.append(player_q2class(p_attrs))

        elif name == "game":
            self.obj_depth.append(game_q2class(p_attrs))

        elif name == "intro":
            self.obj_depth.append(intro_q2class(p_attrs))

        elif name == "item":
            self.obj_depth.append(item_q2class(p_attrs))

        elif name == "include":
            self.obj_depth.append(include_q2class(p_attrs))

        self.char_buffer = []
        self.last_processed = "start"

    def endElement(self, name): # need to append the node that is closing in the right place
        """Override base class ContentHandler method"""
        name = clean_node_name(name)

        if (len(self.char_buffer) != 0) and (self.last_processed == "start"):
            self.obj_depth[-1].value = "".join(self.char_buffer)

        if name == "":
            raise ValueError("XML Node name cannot be empty")

        elif name == "enemy":
            self.obj_depth[-2].enemy.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "door":
            self.obj_depth[-2].door.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "room":
            self.obj_depth[-2].room.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "level":
            self.obj_depth[-2].level.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "text":
            self.obj_depth[-2].text.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "treasure":
            self.obj_depth[-2].treasure.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "interactable":
            self.obj_depth[-2].interactable.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "ending":
            self.obj_depth[-2].ending.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "player":
            self.obj_depth[-2].player.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "game":
            # root node is not added to a parent; stays on the "stack" for the return_object
            self.char_buffer = []
            self.last_processed = "end"
            return

        elif name == "intro":
            self.obj_depth[-2].intro.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "item":
            self.obj_depth[-2].item.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "include":
            self.obj_depth[-2].include.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        self.last_processed = "end"


    def characters(self, in_chars):
        """Override base class ContentHandler method"""
        self.char_buffer.append(in_chars)

    def endDocument(self):
        """Override base class ContentHandler method"""
        self.return_q.put(self.obj_depth[-1])

def obj_wrapper(xml_stream):
    """Call the handler against the XML, then get the returned object and pass it back up"""
    try:
        return_q = Queue.Queue()
        xml.sax.parseString(xml_stream, NodeHandler(return_q))
        return (True, return_q.get())
    except Exception, e:
        return (False, (Exception, e))



