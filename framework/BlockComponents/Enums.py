class BlockStatus: UNCONFIGURED, \
                   READY, \
                   RUNNING, \
                   ERROR, \
                   STARTED = range(5)

class BlockType:    SOURCE, \
                    SINK, \
                    TRANSFORM = range(3)

class ChannelType:  STREAM, \
                    VALUE,\
                    MATRIX = range(3)

class PortType: OUT, \
                IN = range(2)