MaxControl
==========

MaxControl is a work in progress Python library for the Max! wireless heating control system.

You'll need a [Max! Cube LAN Gateway](http://www.amazon.de/gp/product/B00DUED4JM/ref=as_li_ss_tl?ie=UTF8&camp=1638&creative=19454&creativeASIN=B00DUED4JM&linkCode=as2&tag=lukaskleinc00-21) and at least one [thermostat](http://www.amazon.de/gp/product/B005MXAB6S/ref=as_li_ss_tl?ie=UTF8&camp=1638&creative=19454&creativeASIN=B005MXAB6S&linkCode=as2&tag=lukaskleinc00-21).

After some investigation on my own I stubled upon [digit's post in the domoticaforum](http://www.domoticaforum.eu/viewtopic.php?f=66&t=6654) who has already done a lot of the reversing work.

At the moment the library only supports writing permanent temperature changes, i.e. there's no support for timed events yet.

ToDo
----

This code is far from perfect. This still needs to be done:

- [x] Support for multiple rooms / devices in the metadata response
- [ ] Implement all the timetable features
- [ ] Clean up code, document everything

Example
-------
```python
>>> from maxcontrol import MaxControl
>>> mc = MaxControl('192.168.178.26', 62910)
>>> mc.read_values()
{'KHA0007570': {'name': 'Window', 'link_status': 'Ok', 'battery': 'Ok', 'celsius': 20, 'valve_percent': 0, 'program': 'Manual', 'rfaddr': 'CQPq', 'room': '11'}}
>>> mc.rooms
{'11': "Lukas' Room"}
>>> mc.set_temperature('CQPq', 22)
>>> mc.read_values()
{'KHA0007570': {'name': 'Window', 'link_status': 'Ok', 'battery': 'Ok', 'celsius': 22, 'valve_percent': 0, 'program': 'Manual', 'rfaddr': 'CQPq', 'room': '11'}}
>>> mc.system_information
{'hwaddr': '07439c', 'serial_number': 'KHA0007960', 'version': '0113'}
```
