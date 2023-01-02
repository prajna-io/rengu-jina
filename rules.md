
* foreach entry

    ? check invalid tag
    ? check tag type is Dict, List, Scalar, UUID, Date
    * standardize date format



* foreach **.SeeAlso **.References **.Variants 
    ? check is not list
        ! make list
    ? has Body
        ? check not Source
            * addparent Source
        ? check not By
            * addparent Source.By
        * make new fragment
    
        
    * process each 

* foreach **.Source
    ? check no ID
        lookup ID by Title, By
        elif lookup by Title, Media=prime
        elif lookup by Title
        else create new Source
   if not exist, create and link back ID 



convert copyright to date
fragment date is date of oldest source
fragment date is oldest date of creator
