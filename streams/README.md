# Stream Module

[nodes](nodes) contains a list of files, each representing the logic for a single stream.

A stream can be thought of as a destination for a set of detected classes. Plastic bottles, for example, may be routed to the 'plastic' stream, along with other plastics. If desired, a new stream could be created specifically for plastic bottles, which would separate plastic bottles from the rest of the plastic stream.

Streams are intended to be as flexible and customizable as possible to allow the user to specify the exact sorting logic based on the streams available in their locality. For example, the 'compost' stream is provided as a default stream, and collects food, papers, and various organic materials. If your locality does not have a compost stream, the compost stream file can be deleted, effectively removing the stream, and items that normally would be routed to the compost stream will be routed to the default stream ('trash')

For finer tuning, individual label classes can be routed to certain streams. For example, the 'compost.json' stream accepts all items with a label or inherited label of 'food'. If you look at labels/nodes/orange.json, which has a parent class of 'food', its stream is overriden as 'trash' because oranges are generally dissuaded from being composted due to their effects on worms. If your locality does not use worms in their composting stream, you may remove the override to include oranges in the compost stream. This provides easy flexibility to define which classes get sorted into which streams, and allows for as many or as few streams as desired.


### Syntax

**name** - Stream name

```
{
    "name" : "example stream"
}
```

**filter** - Set of of filters which capture class specifications and filter their stream after detection.

**"field"** : { ... }  
    - **operation** : operation to perform on   comparison  
        * "is" include if the field is included in "value" list  
        * "exclude" exclude if the field is included in "value"  
    - **value** : value to perform **operation** on, as single value or list of values   
    - **defer** : if the filter is not satisfied, defer the stream type to the provided value  


```
// plastic.json - accept all objects of class 'plastic' into the plastic stream; however, treat 'plastic straw' and 'plastic bottle cap seal' as trash and defer them to the 'trash' stream.
{
    "name" : plastic
    "filter" : {
        "class" : {
            "operation" : "exclude",
            "value" : ["plastic straw", "plastic bottle cap seal"],
            "defer" : "trash"
        }
    }
}
```

