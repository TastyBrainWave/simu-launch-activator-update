# Introduction

In order to run migrations with FastAPI, we have to use something called Alembic which kind of works similarly to Django, however it isn't as automated as the Django Migrations.

# Prerequisites

We need to install the Alembic package, which will already be part of the requirements.txt file

# Making a migration

At the time of writing this, there is a manual way, but also an automatic way. However, the automatic way seems to not want to work? Not sure why..

## Manually

In order to create a new migration, we neeed to run the following command:

```
alembic revision -m "<revision_name>"
```

This will create a migration file under `alembic/versions/<auto_generated_revision_id>_<revision_name>.py`

In this file, the structure will look similar to this:

```
from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
```

In order to make new tables, we have to individually write the command to create or delete them, similar to the example below:

```
def upgrade():
    op.create_table(
        'songs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String()),
        sa.Column('length', sa.Integer())
        )


def downgrade():
    op.drop_table('songs')
```

After we've written the "migrations", we are ready to migrate!

## The automatic way

The automatic way is super easy:

```
alembic revision --autogenerate
```

And it will do all the work for you, just like Django! I have already configured the path to the models, but in case that changes over time, you need to edit the following to point to the `models.py` file for the SQL Database Models:

```
# add your model's MetaData object here
# for 'autogenerate' support
from sql_app import models
target_metadata = [models.Base.metadata]
```

# Running a migration

In order to run the migration, simply type the following, at it will all be managed by Alembic:

```
alembic upgrade head
```

This applies all the migrations to the database.

# End notes

And that's it! I have pretty much done all the configuration before hand so you don't have to, but left some useful notes in case you need to do it all again. Also, below you can find some of the tutorials for this.

## Credits to:

https://learn.co/lessons/sqlalchemy-alembic-migrations
https://medium.com/@sutharprashant199722/how-to-use-alembic-for-your-database-migrations-d3e93cacf9e8
https://alembic.sqlalchemy.org/