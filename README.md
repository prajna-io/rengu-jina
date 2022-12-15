
# Overview of Data

### Entities

all objects are of type "Entity"

required fields:

  * \_id = a UUID
  * \_type = a more descriptive type
  * \_history = a list of modification entries in the format "user {timestamp}"
  * \_aclr = a list of users and groups allowed to read, always includes @CREATOR
  * \_aclw = a list of users and groups allowed to write, always includes @CREATOR
  
other optional fields are

  * values = simple key/value pairs
  * spans = a reference to a spanned (indexed) field
  * documents = a reference to a content field that is indexed against spans

### Spans

this includes all Term, Creator, and Work entities

required fields:

  * Name = the most common name, or a reference name
  * \_slugs = a list of all variant values of this entity's name, including aliases, slugged (and slugged and stemmed where appropriate)

optional fields:

  * Aliases = all the other versions of the name

### Documents

This includes all open content like content body, description, comment, note, etc.

  * \_id = a hash of the Body
  * Body = the content of the document
  * \_spans = All found spans with hints (e.g. creator_type for creators, locus or page for work)


