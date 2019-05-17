# sqlextras

## Summary

Easily manage custom SQL migrations in Django

## Concept of Operation

Django provides a fairly complete out-of-the-box solution for creating web applications.  That solution is
more complete than Spring (Java) or Flask, which both require an add-on ORM, and add-on logic for handling
static files.

One place where that solution is not complete is in handling database migrations for views, functions, 
and stored procedures. This makes sense - these are not ideally managed in Django.

This package makes that process easier, but makes a few assumptions:

* Developers want to use Django migrations, and so a file that has already been added as a 
  migration should not be modified. If developers do this by accident, or out of habit, they want
  this module to remind them not to do so.

* In developing these migrations, the developer wants to be able to use the IDE capabilities, 
  or command line:
   
      cat my_new_function.sql | manage.py dbshell

* However, the SQL file does not load other files to get its work done.
  That is why there are multiple migrations.


## Specific capabilities

This package will provide the following abstractions:

### `sqlextras.types.SQLFile`

A simple, frozen object with the following properties:

  * *path* - path to a file, assumed to be relative to `settings.BASE_DIR`
  * *sha1sum* - an checksum that will be verified against the files contents

Some methods may be provided that assist in the other abstractions below.  


### `sqlextras.operations.RunSQLFile`

This operation will support the following arguments:

  * *file* - an instance of `SQLFile` above.
  
And keywords arguments:

  * *backards_file* - an optional instance of `SQLFile` above, defaults to `None`
  * *state_operations* - see `django.db.migrations.operations.RunSQL`, defaults to `None`
  * *hints* - see `django.db.migrations.operations.RunSQL`, defaults to `None`.
  * *elidable* - see `django.db.migrations.operations.RunSQL`, defaults to `False`
  * *dbshell* - a flag indicating whether this operation should be run through the 
                backend's command-line, which defaults to `False`.
  
The operation makes an attempt to verify the assumptions given above, verifying the check-sum
when the operation is created, e.g. at import time.  This is before the migration, but should not
affect normal operation of a Django server, only causing problems when running migrations, 
showing migrations, and creating new migration operations.

### `makesqlmigrate`

This is a management command that creates migrations using the operation above.

It supports the following positional parameters:

  * *app* - the Django app for the migration.
  * *path* - the path to the sql file to use forward.
  * [ *backwards_path* ] - an optional backwards path the sql to use forward.

And the following flags:

  * *--dbshell* - indicates that this operation should be run through the database shell.
  * *--name* or *-n* - an optional name for the migration

More flags bay be added, but this is the minimum viable product.

## Stretch Goals/Future Directions

* If *dbshell* is `True`, verify that the file contains nothing like the following:

        START other_file.sql
        \i other_file.sql
        @other_file.sql 
    
* Use `sqlparse` to look for DDL statements in the file, and come up with a good name 
  for the migration.   See `sqlextras.sql` for some general ideas.

* Use `sqlparse` to look for DDL from all such migrations, so that additional management
  commands can print the relations, e.g. TABLE, VIEW, FUNCTION, PROCEDURE, INDEX objects that
  are expected in your database.   See `sqlextras.sql` for some limited developed ideas. 
