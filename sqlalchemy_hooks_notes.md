# HOOKS NOTES


When you save (commit) an object to a table with SQLAlchemy, several "hooks" (events) are triggered.
Here's a list of the most relevant events and the approximate order in which they are called:

**before_flush**: Triggered before the session starts to "flush" the objects in the current transaction. This is the moment where changes made to objects in the session are prepared to be sent to the database, but before the actual queries are executed.

**flush_before_exec**: Triggered right before a "flush" query is executed during the flush operation.

**after_flush**: Triggered after all "flush" operations have been carried out, but before the transaction is actually committed.

**before_commit**: Triggered right before the transaction is committed. If you raise an exception in this event, the transaction will be aborted and a rollback will be executed.

**before_exec**: Triggered before an actual SQL query is executed.

**after_exec**: Triggered after an SQL query has been executed.

**after_commit**: Triggered after the transaction has been successfully committed.

**after_transaction_end**: Triggered when a transaction (either commit or rollback) ends.

**after_soft_rollback** (only in SQLAlchemy >= 1.4): Triggered after a "soft rollback" that doesn't involve an actual database-level transaction.

**after_rollback**: Triggered after a rollback has been executed.