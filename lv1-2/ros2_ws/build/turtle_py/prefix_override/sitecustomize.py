import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/pa2/git/physicalai-lv1-assignments/lv1-2/ros2_ws/install/turtle_py'
