# hass_fan_switch
Fan Swithc platform for Home Assistant

## How it works
This custom component adds a fan switch platform similar to the light switch platform

## Configuration
This component adds a fan_switch platform that functions similar to the light switch platform

example configuration:
```
fan:
- platform: fan_switch
  name: Small Fan
  entity_id: switch.fan_switch
```

### Configuration Variables ###
<dl>
 <dt>name</dt>
 <dd>
  <i>(string)(Optional)</i><br/>The name of the fan switch.
  <br/><br/>
  <i>Default value:</i><br/>Fan Switch
 </dd>
 <dt>entity_id</dt>
 <dd>
  <i>(string)(Required)</i><br/>The entity_id of a switch entity to control as a fan.
 </dd>
</dl>

A fan switch only supports turing on/off a fan.
