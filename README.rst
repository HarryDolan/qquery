qquery
======

This package provides a simple interface for reading Quicken For Mac databases.  It inlcudes both a
python module and a command line interface.

Locating the Database
---------------------

Quicken For Mac keeps its user files in ``~/Library/Application Support/Quicken 2017``.
In that directory the database file is in ``Documents/Qdata.quicken2017/data`` (or thereabouts).
For safety, do not operate directly on this file.  Make a copy as, for example: ::

   # cd '~/Library/Application Support/Quicken 2017'
   # cd Documents/Qdata.quicken2017
   # cp data /tmp/copyofqdata
   # cd /tmp
   # file copyofqdata 
   copyofqdata: SQLite 3.x database, last written using SQLite version 3019003

The output of the last command verifies that the file is an ``sqlite`` database.

Command Line Tool
-----------------

The command line tool, also called ``qquery``, provides a simple, convenient interface to the database.
It offers many options, all of which are described with the --help switch: ::

  # qquery --help

Here are some examples.

List all accounts: ::

  # qquery --qdb=copyofqdata --list-accounts

List all categories:  ::

  # qquery --qdb=copyofqdata --list-categories

List all transactions (this can create a lot of output):  ::

  # qquery --qdb=copyofqdata --list-transactions

List only transations from account "First National", category "Charity", posted during the year 2016: ::

  # qquery --qdb=copyofqdata --list-transactions \
           --restrict-to-accounts="First National" \
           --restrict-to-categories="Charity" \
	   --date-from=2016-01-01 --date-to=2016-12-31

Report on the balances (including details of secuities) of all accounts as of December 31, 2016.
(Accounts with zero balance will not be listed): ::

  # qquery --qdb=copyofqdata --report-holdings --date-to=2016-12-31

Python module
-------------

The module may be included in python programs in the the usual way.  Help is also available.
Use the following to get a list of all available functions: ::

  >>> import qquery
  >>> help (qquery)

Here is how to list all accounts using the iterator provided by the function ``getAccounts()``.
Each pass through the loop returns a dictionary for each account: ::

  >>> import qquery as qq
  >>> qq.open ('copyofqdata')
  >>> for account in qq.getAccounts():
  ...     print account
  ... 

Similarly, this is how to list all categories by using the iterator provided by the function
``getCategories()``.
Each pass through the loop returns a dictionary for each category: ::

  >>> import qquery as qq
  >>> qq.open ('copyofqdata')
  >>> for category in qq.getCategories():
  ...     print category
  ... 

And for all transactions using ``getTransactions()``: ::

  >>> import qquery as qq
  >>> qq.open ('copyofqdata')
  >>> for trans in qq.getTransactions():
  ...     print trans
  ... 

There are many fields supplied with each ``trans`` dictionary, so the above will produce
a lot of output.  One may instead choose to examine only some of those fields as in ::

  >>> import qquery as qq
  >>> qq.open ('copyofqdata')
  >>> for trans in qq.getTransactions():
  ...     print trans['date'], trans['amount'], trans['payeeName']
  ... 

This can be further refined using the **setRestrictTo** functions, for example: ::

  >>> import qquery as qq
  >>> qq.open ('copyofqdata')
  >>> qq.setRestrictToAccounts ('First National')
  >>> qq.setRestrictToCategories ('Charity,Gifts')
  >>> qq.setRestrictToDates (dateFrom='2016-01-01', dateTo='2016-12-31')
  >>> for trans in qq.getTransactions():
  ...     print trans['date'], trans['amount'], trans['payeeName']
  ... 


Next Steps
----------

This is a lot more information in the Quicken database than is exposed through this interface.
Requests for feature enhancements are welcome.
