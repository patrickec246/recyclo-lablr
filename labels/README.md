# Label Module

[nodes](nodes) contains a list of files, each representing the functionality of a single class during detection.

### Syntax

**inherit**: Inherits a set of fields from parent classes. Use "all" to inherit all un-implemented fields for a node. Provide a list to inherit only certain fields. The label processor will walkup the inheritance tree until it finds a parent that occludes ownership of a field. Fields which cannot be deduced from any parent are left blank.

```
// Inherit all fields from the closest parent with the field available.
{
    "inherit" : "all"
}

// Inherit only the "RIC" field from the closest parent with the "RIC" field available.
{
    "inherit" : ["RIC"]
}
```

**parent**: Parent class name. The label processor will create an inheritance connection from the node to the parent node. Leave blank if top-level class.

```
FILE: plastic-soda-bottle.json:

{
    "parent" : "plastic bottle"
}
```

**RIC**: **R**esin **I**dentification **C**ode possible classes as a list. This field is used to guide the detector if resin detection capabilities are not present.
```
{
    "RIC" : [1, 2, 7]
}
```