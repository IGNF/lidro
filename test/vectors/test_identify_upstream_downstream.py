from typing import Dict

from shapely.geometry import Point

from lidro.create_virtual_point.vectors.identify_upstream_downstream import (
    identify_upstream_downstream,
)


def test_identify_upstream_downstream_default():
    # Example list of points
    points = [
        {"geometry": Point(830211.190425319829956, 6292000.43919328507036), "z_q1": 2.95},
        {"geometry": Point(830211.950744876405224, 6291980.453650656156242), "z_q1": 3.05},
        {"geometry": Point(830212.711064432864077, 6291960.468108027242124), "z_q1": 3.20},
        {"geometry": Point(830213.471383989439346, 6291940.482565398328006), "z_q1": 3.15},
        {"geometry": Point(830214.231703546014614, 6291920.497022769413888), "z_q1": 3.22},
        {"geometry": Point(830214.992023102473468, 6291900.511480140499771), "z_q1": 4.12},
        {"geometry": Point(830218.033301328658126, 6291820.569309624843299), "z_q1": 4.12},
        {"geometry": Point(830218.793620885233395, 6291800.583766995929182), "z_q1": 4.55},
        {"geometry": Point(830219.553940441692248, 6291780.598224367015064), "z_q1": 4.54},
        {"geometry": Point(830224.663624010980129, 6291680.817003472708166), "z_q1": 5.00},
        {"geometry": Point(830228.343047266826034, 6291661.158370648510754), "z_q1": 5.05},
        {"geometry": Point(830232.022470522555523, 6291641.499737825244665), "z_q1": 5.05},
        {"geometry": Point(830246.740163545822725, 6291562.865206529386342), "z_q1": 5.10},
        {"geometry": Point(830250.419586801668629, 6291543.20657370518893), "z_q1": 5.15},
        {"geometry": Point(830254.099010057398118, 6291523.547940881922841), "z_q1": 2.95},
        {"geometry": Point(830257.778433313244022, 6291503.88930805772543), "z_q1": 2.96},
        {"geometry": Point(830261.457856569089927, 6291484.230675233528018), "z_q1": 6.00},
        {"geometry": Point(830265.137279824819416, 6291464.572042410261929), "z_q1": 6.10},
        {"geometry": Point(830268.81670308066532, 6291444.913409586064517), "z_q1": 6.15},
        {"geometry": Point(830272.496126336511225, 6291425.254776761867106), "z_q1": 6.10},
        {"geometry": Point(830287.621702362317592, 6291346.699770421721041), "z_q1": 7.00},
    ]

    upstream, downstream = identify_upstream_downstream(points)

    assert isinstance(upstream, Dict)
    assert isinstance(downstream, Dict)
    assert upstream["geometry"] == Point(830211.1904253198, 6292000.439193285)
    assert upstream["z_q1"] == 2.95
    assert downstream["geometry"] == Point(830287.6217023623, 6291346.699770422)
    assert downstream["z_q1"] == 7.0
